import os
import json
import argparse
from google import genai
from google.genai import types

try:
    from duckduckgo_search import DDGS
    HAS_DDGS = True
except ImportError:
    HAS_DDGS = False



SYSTEM_PROMPT = """You are an advanced Fake News Detection AI. Your task is to analyze news articles, headlines, social media posts, or claims and determine their credibility.

Identify factual claims made in the content.
Check for sensational language, lack of sources, and logical inconsistencies.

Classify the news into one of the following categories:
Real News, Likely Real, Suspicious, Likely Fake, Fake News

Output Format:
{
  "article_summary": "A concise 2-3 sentence summary of the article's main claims.",
  "classification": "...",
  "credibility_score": 0,
  "sentiment": "Emotional tone (e.g., Fear-mongering, Joy, Neutral)",
  "bias": "Detected political or commercial bias",
  "xai_explanation": "A 1-2 sentence explanation of exactly WHY the AI made this prediction",
  "risk_indicators": [
    "List of risk factors..."
  ],
  "fact_check_findings": [
    {
      "claim": "Specific claim made in text",
      "status": "Supported / Unverified / Refuted"
    }
  ],
  "source_verification": [
    {
      "source": "Name of source (e.g. Reuters, WHO, or unknown blog)",
      "status": "Verified / Unverified / Highly Suspicious"
    }
  ]
}"""

def get_fact_check_context(news_text: str, client: genai.Client) -> str:
    if not HAS_DDGS:
        return "DuckDuckGo Search is not installed."
    
    try:
        query_prompt = f"Extract a concise search query (max 5 words) to fact-check the following claim or news:\n\n{news_text}\n\nSearch Query:"
        query_response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=query_prompt,
        )
        query = query_response.text.strip().replace('"', '').replace("'", "")
        
        print(f"Fact-checking web query: '{query}'...")
        results = DDGS().text(query, max_results=3)
        
        if not results:
            return "No relevant search results found."
        
        context = "Recent Web Search Results:\n"
        for i, res in enumerate(results):
            context += f"{i+1}. {res.get('title', '')}: {res.get('body', '')}\n"
        
        return context
    except Exception as e:
        return f"Error during web search: {e}"

def analyze_news(news_text: str, use_search: bool = True, provided_api_key: str = None) -> str:
    api_key = provided_api_key or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("API Key is missing! Please provide your Google Gemini API key.")
    
    # Initialize the new SDK Client
    client = genai.Client(api_key=api_key)

    # Fetch web context if enabled
    web_context = ""
    if use_search and HAS_DDGS:
        web_context_text = get_fact_check_context(news_text, client)
        web_context = f"\n\n[Web Fact-Check Context]\n{web_context_text}"
        print("Web context gathered successfully.\n")
    elif use_search and not HAS_DDGS:
        print("Warning: duckduckgo-search not installed. Skipping web fact-checking.\n")

    prompt = f"Input:\n{news_text}{web_context}\n\nAnalyze the content and return the result in the specified format."
    
    response = client.models.generate_content(
        model='gemini-1.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
        )
    )
    
    return response.text

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Advanced Fake News Detector using Gemini AI")
    parser.add_argument("--text", type=str, help="The news text to analyze")
    parser.add_argument("--file", type=str, help="Path to a text file containing the news text")
    parser.add_argument("--no-search", action="store_true", help="Disable real-time web search fact-checking")
    
    args = parser.parse_args()
    
    news_text = ""
    if args.text:
        news_text = args.text
    elif args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                news_text = f.read()
        except FileNotFoundError:
            print(f"Error: File '{args.file}' not found.")
            exit(1)
    else:
        print("Please provide either --text or --file argument.")
        parser.print_help()
        exit(1)
        
    try:
        result_json = analyze_news(news_text, use_search=not args.no_search)
        parsed_json = json.loads(result_json)
        print(json.dumps(parsed_json, indent=2))
    except Exception as e:
        print(f"Error during analysis: {e}")

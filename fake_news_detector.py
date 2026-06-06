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

# Check for API key at the top
api_key = os.environ.get("GEMINI_API_KEY")

SYSTEM_PROMPT = """You are an advanced Fake News Detection AI. Your task is to analyze news articles, headlines, social media posts, or claims and determine their credibility.

Instructions:

Read the provided news text carefully.
Identify factual claims made in the content.
Check for:
- Sensational or emotionally charged language
- Lack of credible sources
- Logical inconsistencies
- Clickbait headlines
- Misleading statistics or data

Additionally, perform the following advanced analyses:
1. **Sentiment Analysis**: Analyze the emotional tone (e.g., Fear-mongering, Outrage, Neutral, Joy).
2. **Bias Detection**: Classify any political, commercial, or ideological bias.
3. **Source Credibility**: Estimate a source credibility score (0-100) based on the text's formatting, claims, and any mentioned sources.
4. **Explainable AI (XAI)**: Provide a structured breakdown detailing your reasoning across different dimensions (lexical analysis, factual consistency, logical flow).

Classify the news into one of the following categories:
Real News, Likely Real, Suspicious, Likely Fake, Fake News

Provide a confidence score (0-100%).
Suggest trusted sources or fact-checking methods for verification.
If the input includes [Web Fact-Check Context], use those search results to evaluate the factual consistency of the claims.

Output Format:
{
  "classification": "...",
  "confidence_score": 0,
  "sentiment": "...",
  "bias": "...",
  "source_credibility_score": 0,
  "xai_explanation": {
    "lexical_analysis": "...",
    "factual_consistency": "...",
    "logical_flow": "..."
  },
  "key_indicators": [],
  "reasoning": "...",
  "verification_suggestions": []
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

def analyze_news(news_text: str, use_search: bool = True) -> str:
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set. Please set it to your Google Gemini API key.")
    
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

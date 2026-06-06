import os
import json
import argparse
import google.generativeai as genai

# Configure the API key
# Make sure to set the GEMINI_API_KEY environment variable
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

SYSTEM_PROMPT = """You are an advanced Fake News Detection AI. Your task is to analyze news articles, headlines, social media posts, or claims and determine their credibility.

Instructions:

Read the provided news text carefully.
Identify factual claims made in the content.
Check for:
Sensational or emotionally charged language
Lack of credible sources
Logical inconsistencies
Clickbait headlines
Misleading statistics or data
Classify the news into one of the following categories:
Real News
Likely Real
Suspicious
Likely Fake
Fake News
Provide a confidence score (0–100%).
Explain the reasoning behind the classification.
Highlight specific phrases or statements that influenced the decision.
Suggest trusted sources or fact-checking methods for verification.

Output Format:

{
  "classification": "Likely Fake",
  "confidence_score": 87,
  "key_indicators": [
    "No credible sources cited",
    "Highly emotional language",
    "Extraordinary claim without evidence"
  ],
  "reasoning": "The article makes significant claims without providing verifiable evidence or references to trusted organizations.",
  "verification_suggestions": [
    "Check Reuters",
    "Check AP News",
    "Search official government sources"
  ]
}"""

def analyze_news(news_text: str) -> str:
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set. Please set it to your Google Gemini API key.")
    
    # Use Gemini 1.5 Flash for fast text analysis
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=SYSTEM_PROMPT,
        generation_config={"response_mime_type": "application/json"}
    )
    
    prompt = f"Input:\n{news_text}\n\nAnalyze the content and return the result in the specified format."
    
    response = model.generate_content(prompt)
    return response.text

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fake News Detector using Gemini AI")
    parser.add_argument("--text", type=str, help="The news text to analyze")
    parser.add_argument("--file", type=str, help="Path to a text file containing the news text")
    
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
        result_json = analyze_news(news_text)
        # Parse and pretty print the JSON
        parsed_json = json.loads(result_json)
        print(json.dumps(parsed_json, indent=2))
    except Exception as e:
        print(f"Error during analysis: {e}")

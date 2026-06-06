# Fake News Detector

An AI-powered tool that analyzes news articles, headlines, social media posts, or claims to determine their credibility using Google's Gemini API.

## Advanced Features

This project includes advanced data science capabilities:
- **Sentiment Analysis**: Detects the emotional tone (e.g., Fear-mongering, Outrage, Joy).
- **Bias Detection**: Identifies political, commercial, or ideological bias.
- **Source Credibility Scoring**: Estimates source credibility (0-100).
- **Explainable AI (XAI)**: Provides a structural breakdown (lexical, factual, logical) detailing the reasoning behind the classification.
- **Real-Time Fact-Checking**: Automatically searches the web for recent context to verify the claims using DuckDuckGo.

## Setup

1. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set your Gemini API key as an environment variable:
   - On Windows (Command Prompt): `set GEMINI_API_KEY=your_api_key`
   - On Windows (PowerShell): `$env:GEMINI_API_KEY="your_api_key"`
   - On Linux/Mac: `export GEMINI_API_KEY="your_api_key"`

## Usage

You can pass the text directly via the command line:

```bash
python fake_news_detector.py --text "Your sensational news claim here"
```

Or you can read from a text file:

```bash
python fake_news_detector.py --file article.txt
```

### Disabling Web Search

By default, the script will extract a query from your text and search DuckDuckGo to fact-check the claim. If you want to disable this feature and rely only on the LLM's internal knowledge, use the `--no-search` flag:

```bash
python fake_news_detector.py --text "Your news claim" --no-search
```

# Fake News Detector

An AI-powered tool that analyzes news articles, headlines, social media posts, or claims to determine their credibility using Google's Gemini API.

## Advanced Features

This project includes advanced data science capabilities:
- **Sentiment Analysis**: Detects the emotional tone (e.g., Fear-mongering, Outrage, Joy).
- **Bias Detection**: Identifies political, commercial, or ideological bias.
- **Source Credibility Scoring**: Estimates source credibility (0-100).
- **Explainable AI (XAI)**: Provides a structural breakdown (lexical, factual, logical) detailing the reasoning behind the classification.
- **Real-Time Fact-Checking**: Automatically searches the web for recent context to verify the claims using DuckDuckGo.
- **Premium Web Interface**: A stunning, modern web application built with Flask and Glassmorphism design.

## Setup

1. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set your Gemini API key as an environment variable:
   - On Windows (Command Prompt): `set GEMINI_API_KEY=your_api_key`
   - On Windows (PowerShell): `$env:GEMINI_API_KEY="your_api_key"`
   - On Linux/Mac: `export GEMINI_API_KEY="your_api_key"`

## Usage (Web Application)

To run the web interface locally, execute:

```bash
python app.py
```

Then, open your web browser and navigate to the localhost URL:
**http://127.0.0.1:5000**

You can paste your news text directly into the web UI, and toggle the Live Web Fact-Checking feature.

## Usage (Command Line)

You can still use the script via the command line:

```bash
python fake_news_detector.py --text "Your sensational news claim here"
```

Or disable live web search from the CLI:

```bash
python fake_news_detector.py --text "Your claim" --no-search
```

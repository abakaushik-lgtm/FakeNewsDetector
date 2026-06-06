# Fake News Detector

An AI-powered tool that analyzes news articles, headlines, social media posts, or claims to determine their credibility using Google's Gemini API.

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

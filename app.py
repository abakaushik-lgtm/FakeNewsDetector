from flask import Flask, render_template, request, jsonify
from fake_news_detector import analyze_news
import json
import re

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400
    
    news_text = data['text']
    use_search = data.get('use_search', True)
    api_key = data.get('api_key', None)
    
    try:
        # analyze_news returns a JSON string from Gemini
        result_str = analyze_news(news_text, use_search=use_search, provided_api_key=api_key)
        
        # Clean up markdown code blocks if the LLM outputted them
        match = re.search(r'\{.*\}', result_str, re.DOTALL)
        if match:
            result_str = match.group(0)
            
        try:
            result_dict = json.loads(result_str.strip())
        except json.JSONDecodeError:
            # Fallback if Gemini refused to output JSON (e.g., safety filters)
            result_dict = {
                "classification": "Error Parsing Output",
                "confidence_score": 0,
                "reasoning": f"Raw Output from AI: {result_str}",
                "key_indicators": ["Output was not valid JSON"],
                "verification_suggestions": ["Try again or check API keys/safety settings"]
            }
        return jsonify(result_dict)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

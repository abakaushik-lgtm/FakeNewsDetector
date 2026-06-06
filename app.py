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
    
    try:
        # analyze_news returns a JSON string from Gemini
        result_str = analyze_news(news_text, use_search=use_search)
        
        # Clean up markdown code blocks if the LLM outputted them
        match = re.search(r'\{.*\}', result_str, re.DOTALL)
        if match:
            result_str = match.group(0)
            
        result_dict = json.loads(result_str.strip())
        return jsonify(result_dict)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

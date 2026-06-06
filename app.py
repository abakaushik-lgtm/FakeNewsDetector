from flask import Flask, render_template, request, jsonify
from fake_news_detector import analyze_news
import json
import re
import requests
from bs4 import BeautifulSoup
import PyPDF2
from io import BytesIO

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def extract_text_from_url(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    paragraphs = soup.find_all('p')
    text = ' '.join([p.get_text() for p in paragraphs])
    return text[:15000] # Limit to 15k chars to avoid token limits

def extract_text_from_pdf(file_stream):
    pdf_reader = PyPDF2.PdfReader(file_stream)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text[:15000]

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    # Handle FormData instead of JSON
    mode = request.form.get('mode', 'text')
    use_search = request.form.get('use_search', 'true').lower() == 'true'
    api_key = request.form.get('api_key', None)
    
    news_text = ""
    
    try:
        if mode == 'text':
            news_text = request.form.get('text', '')
            if not news_text:
                return jsonify({'error': 'No text provided'}), 400
        elif mode == 'url':
            url = request.form.get('url', '')
            if not url:
                return jsonify({'error': 'No URL provided'}), 400
            news_text = extract_text_from_url(url)
            if not news_text.strip():
                return jsonify({'error': 'Could not extract text from the URL.'}), 400
        elif mode == 'file':
            if 'file' not in request.files:
                return jsonify({'error': 'No file uploaded'}), 400
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
                
            if file.filename.lower().endswith('.pdf'):
                news_text = extract_text_from_pdf(BytesIO(file.read()))
            else:
                news_text = file.read().decode('utf-8')[:15000]
                
            if not news_text.strip():
                return jsonify({'error': 'Could not extract text from the file.'}), 400
        else:
            return jsonify({'error': 'Invalid mode'}), 400
    except Exception as e:
        return jsonify({'error': f"Failed to extract input: {str(e)}"}), 400
        
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
                "credibility_score": 0,
                "sentiment": "N/A",
                "bias": "N/A",
                "xai_explanation": "The AI model encountered an error or its output was blocked by safety filters.",
                "risk_indicators": ["Output was not valid JSON", f"Raw Output from AI: {result_str}"],
                "fact_check_findings": [],
                "source_verification": []
            }
        return jsonify(result_dict)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

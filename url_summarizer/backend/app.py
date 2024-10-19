from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
# from gensim.summarization import summarize
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
def extract_content(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    text_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'div', 'span', 'article'])
    text_content = ' '.join([element.get_text() for element in text_elements])
    # print(text_content)
    if not text_content.strip():
        return "No meaningful content found."  # Return a message if no content is found
    return text_content.replace('\n','')

def summarize_content(text_content):
    summary = summarize(text, ratio=0.2)
    return summary

def compute_similarity(paragraph1, paragraph2):
    embeddings = model.encode([paragraph1, paragraph2])

    similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    return similarity

@app.route('/api/fetch-url', methods=['POST'])
def fetch_url():
    data = request.get_json()
    url = data.get('url')
    paragraph = data.get('paragraph')

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)
        content = response.text

        extracted_text = extract_content(content)
        print(extracted_text)

        summary = extracted_text
        #summarize_content(extracted_text)
        similarity_score = compute_similarity(paragraph, summary)
        print(similarity_score)
        if similarity_score>0:
            return jsonify({'valid': True, 'summary': " Valid Proper URL "})
        else:
            return jsonify({'valid': True, 'summary': "URL seems to be out of context"})
        
    except requests.exceptions.RequestException as e:
        return jsonify({'valid': False, 'message': str(e)}), 400




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)  # Make it accessible on your local network

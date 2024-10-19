from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
# from gensim.summarization import summarize
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import re

app = Flask(__name__)
CORS(app) 

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
def extract_content(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    text_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'div', 'span', 'article'])
    text_content = ' '.join([element.get_text() for element in text_elements])
    # print(text_content)
    if not text_content.strip():
        return "No meaningful content found."  
    return text_content.replace('\n','')

def summarize_content(text_content):
    summary = summarize(text, ratio=0.2)
    return summary

def compute_similarity(paragraph1, paragraph2):
    embeddings = model.encode([paragraph1, paragraph2])

    similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    return similarity




# @app.route('/api/fetch-url', methods=['POST'])
# def fetch_url():
#     data = request.get_json()
#     url = data.get('url')
#     paragraph = data.get('paragraph')

#     try:
#         response = requests.get(url)
#         response.raise_for_status()  
#         content = response.text

#         extracted_text = extract_content(content)
#         print(extracted_text)

#         summary = extracted_text
#         #summarize_content(extracted_text)
#         similarity_score = compute_similarity(paragraph, summary)
#         print(similarity_score)
#         if similarity_score>0:
#             return jsonify({'valid': True, 'summary': " Valid Proper URL "})
#         else:
#             return jsonify({'valid': True, 'summary': "URL seems to be out of context"})
        
#     except requests.exceptions.RequestException as e:
#         return jsonify({'valid': False, 'message': str(e)}), 400

@app.route('/api/check-url', methods=['POST'])
def fetch_url():
    data = request.get_json()
    text = data.get('text')
    invalid_urls=[]

    try:
        url_pattern = r'(https?://\S+)'
        # match = re.search(url_pattern, text)
        parts=[]
        last_index=0
    
        for match in re.finditer(url_pattern, text):
            # Get the URL
            url = match.group(0)
            start = match.start()
            end = match.end()

            # Text before the URL
            text_before_url = text[last_index:start].strip()
            parts.append({'text_before_url': text_before_url, 'url': url})

            # Update the last index
            last_index = end
        if last_index < len(text):
            text_after_url = text[last_index:].strip()
            parts.append({'text_before_url': text_after_url, 'url': None})
        print(parts)
        for part in parts:
            if part['url']!=None:
                try:
                    response = requests.get(part['url'])
                    content = response.text 
                    contents = extract_content(content)
                    similarity_score = compute_similarity(part['text_before_url'], contents)
                    if similarity_score>0:
                        invalid_urls.append({'url':part['url'],'score':str(similarity_score)})
                        # return jsonify({'valid': True, 'summary': " Valid Proper URL "})
        
                except requests.exceptions.RequestException as e:
                    invalid_urls.append({'url':part['url'],'score':None})
                    print(e)
        print(invalid_urls)
        return {'invalid_urls': invalid_urls}

        
    except requests.exceptions.RequestException as e:
        return {'invalid_urls': 'Failed'}, 400




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)  # Make it accessible on your local network

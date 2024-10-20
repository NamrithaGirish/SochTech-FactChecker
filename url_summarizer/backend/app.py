from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from bespokelabs import BespokeLabs
from bs4 import BeautifulSoup
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import re

app = Flask(__name__)
CORS(app)

# Initialize the Bespoke API client
bl = BespokeLabs(auth_token=os.environ.get("BESPOKE_API_KEY"))

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def extract_content(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    text_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'div', 'span', 'article'])
    text_content = ' '.join([element.get_text() for element in text_elements])
    if not text_content.strip():
        return "No meaningful content found."  
    return text_content.replace('\n', '')

def compute_similarity(paragraph1, paragraph2):
    embeddings = model.encode([paragraph1, paragraph2])
    similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    return similarity

def split_input(input_string):
    parts = input_string.split("ChatGPT said:")
    if len(parts) < 2:
        raise ValueError("Input must contain 'ChatGPT said:' to separate context and claim.")
    context = parts[0].strip()  
    claim = parts[1].strip()
    if claim.startswith("ChatGPT\n"):
        claim = claim.replace("ChatGPT\n", "", 1).strip()
    return context, claim

def get_google_search_results(query, max_retries=3):
    url = f"https://www.google.com/search?q={query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.176 Safari/537.36"
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a')
            urls = [link.get('href') for link in links if link.get('href') and link.get('href').startswith('http') and 'google' not in link.get('href')]
            return urls[:10]  # Return only the first 10 URLs
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
    
    return []  # Return an empty list if all attempts fail

def scrape_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        result = ""
        for para in paragraphs:
            text = para.get_text(strip=True)
            if text:
                result += text + "\n\n"
        return result.strip()  
    except requests.exceptions.RequestException as e:
        print(f"Error scraping {url}: {e}")
        return None

def perform_source_search(text):
    urls = get_google_search_results(text)
    return urls

@app.route('/api/check-url', methods=['POST'])
def fetch_url():
    data = request.get_json()
    invalid_urls = []
    citations = []
    support_prob = 0.0  
    try:
        text = data.get('text')
        if not text:
            return jsonify({'valid': False, 'message': 'Invalid input. URL is required.'}), 400

        context, claim = split_input(text)

        result_urls = get_google_search_results(context)
        context_new = ""
        for rurl in result_urls:
            content_of_url = scrape_url(rurl)
            if content_of_url:
                context_new += content_of_url + " "
        
        print("\nNew Context:", context_new)
        factcheck_response = bl.minicheck.factcheck.create(claim=claim, context=context_new)
        support_prob = float(factcheck_response.support_prob)  

        citations = perform_source_search(claim)  
    except Exception as e:
        print("Error occurred:", str(e))
        return jsonify({'valid': False, 'message': 'An error occurred: ' + str(e)}), 500

    try:
        url_pattern = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
        parts = []
        invalid_lines = [] 
        last_index = 0

        for match in re.finditer(url_pattern, text):
            url = match.group(0)
            start = match.start()
            end = match.end()
            text_before_url = text[last_index:start].strip()
            parts.append({'text_before_url': text_before_url, 'url': url})
        
        claim_lines = claim.splitlines()
        
        for line in claim_lines:
            similarity_score = compute_similarity(line.strip(), context_new.strip())
            if similarity_score < 0.5:
                invalid_lines.append({'line': line.strip(), 'similarity_score': float(similarity_score)})
        
            last_index = end
        
        if last_index < len(text):
            text_after_url = text[last_index:].strip()
            parts.append({'text_before_url': text_after_url, 'url': None})
        
        print(parts)
        for part in parts:
            if part['url'] is not None:
                try:
                    response = requests.get(part['url'])
                    content = response.text 
                    contents = extract_content(content)
                    similarity_score = compute_similarity(part['text_before_url'], contents)
                    if similarity_score > 0:
                        invalid_urls.append({'url': part['url'], 'score': str(float(similarity_score))})
                except requests.exceptions.RequestException as e:
                    invalid_urls.append({'url': part['url'], 'score': None})
                    print(e)

        print(invalid_urls)
        return jsonify({
            'valid': support_prob > 0.5,
            'support_prob': support_prob,
            'invalid_urls': invalid_urls,
            'citations': citations,
            'invalid_lines': invalid_lines  
        })
        
    except requests.exceptions.RequestException as e:
        return {'invalid_urls': 'Failed', 'citation': citations}, 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

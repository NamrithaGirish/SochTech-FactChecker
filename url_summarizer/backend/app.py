from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from bespokelabs import BespokeLabs
from bs4 import BeautifulSoup
# from gensim.summarization import summarize
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

def split_input(input_string):
    # Split the input based on "ChatGPT said:"
    parts = input_string.split("ChatGPT said:")
    
    if len(parts) < 2:
        raise ValueError("Input must contain 'ChatGPT said:' to separate context and claim.")
    
    context = parts[0].strip()  # Part before "ChatGPT said:"
    claim = parts[1].strip() 
    # If the claim starts with "ChatGPT", remove that part
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
            response.raise_for_status()  # Check for HTTP errors
            soup = BeautifulSoup(response.text, 'html.parser')
            
            links = soup.find_all('a')
            urls = [link.get('href') for link in links if link.get('href') and link.get('href').startswith('http') and 'google' not in link.get('href')]
            return urls[:10]  # Return only the first 10 URLs
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(2)  # Wait for 2 seconds before retrying
    
    return []  # Return an empty list if all attempts fail



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
def scrape_url(url, max_paragraphs=1, max_chars=500):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract the first few paragraphs ('p' tags)
        paragraphs = soup.find_all('p')
        result = ""
        paragraph_count = 0
        char_count = 0

        for para in paragraphs:
            text = para.get_text(strip=True)
            
            if text:
                # Accumulate text until reaching the max number of paragraphs or characters
                result += text + "\n\n"
                paragraph_count += 1
                char_count += len(text)

                # if paragraph_count >= max_paragraphs or char_count >= max_chars:
                #     break

        return result.strip()  # Return the extracted content
    except requests.exceptions.RequestException as e:
        print(f"Error scraping {url}: {e}")
        return None

def perform_source_search(text):
    urls  = get_google_search_results(text)
    return urls


@app.route('/api/check-url', methods=['POST'])
def fetch_url():
    data = request.get_json()
    invalid_urls = []
    citations = []
    support_prob = 0.0  # Initialize support probability
    try:
        text = data.get('text')  # Get the text from the request
        if not text:
            return jsonify({'valid': False, 'message': 'Invalid input. URL is required.'}), 400

        # Split the input into context and claim
        try:
            context, claim = split_input(text)
        except ValueError as e:
            return jsonify({'valid': False, 'message': str(e)}), 400

        # Perform Google search and scrape content
        result_urls = get_google_search_results(context)
        context_new = ""
        for rurl in result_urls:
            content_of_url = scrape_url(rurl)
            if content_of_url:
                context_new += content_of_url + " "
        
        print("\nNew Context:",context_new)
        # Call Bespoke API for fact-checking
        factcheck_response = bl.minicheck.factcheck.create(claim=claim, context=context_new)
        support_prob = factcheck_response.support_prob
        
        citations = perform_source_search(claim)  # Get citations
        
        # Check if claim is supported
        # if support_prob > 0.5:
        #     return jsonify({'valid': True, 'support_prob': support_prob, 'invalid_urls': invalid_urls, 'citations': citations})
        # else:
        #     return jsonify({'valid': False, 'support_prob': support_prob, 'invalid_urls': invalid_urls, 'citations': citations})

    except Exception as e:
        print("Error occurred:", str(e))
        return jsonify({'valid': False, 'message': 'An error occurred: ' + str(e)}), 500

    try:
        # url_pattern = r'(https?://\S+)'
        url_pattern = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"

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
        if support_prob > 0.5:
            return jsonify({'valid': True, 'support_prob': support_prob, 'invalid_urls': invalid_urls, 'citations': citations})
        else:
            return jsonify({'valid': False, 'support_prob': support_prob, 'invalid_urls': invalid_urls, 'citations': citations})
        
    except requests.exceptions.RequestException as e:
        return {'invalid_urls': 'Failed','citation':citations}, 400




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

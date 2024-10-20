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


def get_google_search_results(query):
    url = f"https://www.google.com/search?q={query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.176 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract search result links (you may need to adjust this selector)
    links = soup.find_all('a')
    urls = []
    mu=0
    for link in links:
        href = link.get('href')
        # print("0000",href)
        if href and href.startswith("http") and 'google' not in href:
            mu+=1
            urls.append(href)
            if mu==10:
                break
        # try:
        #     if href and 'url?q=' in href:
        #         # Clean the URL
        #         cleaned_url = href.split('url?q=')[1].split('&')[0]
        #         urls.append(cleaned_url)
        #         print("//////",cleaned_url)
        # except Exception as e:
        #     print(e)
    
    return urls



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
def scrape_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract data as needed (customize this part)
        data = soup.find_all(['h1']) # Example: finding all <h1> tags
        result=""
        c=0
        for item in data:
            c=0
            if item.get_text():
                c+=1
                result+=item.get_text()
                if c==3:
                    break
            # print(f"Data from {url}: {item.get_text()}\n")
        # print(result)
        return result
    except requests.exceptions.RequestException as e:
        print(f"Error scraping {url}: {e}")

def perform_source_search(text):
    urls  = get_google_search_results(text)
    return urls


@app.route('/api/check-url', methods=['POST'])
def fetch_url():
    data = request.get_json()
    text = data.get('text')
    invalid_urls=[]
    try:
        data = request.get_json()
        # Log the received data
        print("Received data:", data)

        url = data.get('text')  # This should contain both the context and claim
        if not url:
            return jsonify({'valid': False, 'message': 'Invalid input. URL is required.'}), 400

        # Split the input into context and claim
        try:
            context, claim = split_input(url)
        except ValueError as e:
            return jsonify({'valid': False, 'message': str(e)}), 400

        # Log the separated context and claim
        print("Context:", context)
        print("Claim:", claim)
        query = context
        result_urls = get_google_search_results(query)
        contextnew=""
        print("Final urls : ",result_urls)
        hm=0
        for rurl in result_urls:
            # print("hello")
            contentofurl=scrape_url(rurl)
            if contentofurl:
                hm+=1
                contextnew+=contentofurl
                if hm==10:
                    break
        print("New context : ",contextnew)
        # Call Bespoke API for fact-checking
        factcheck_response = bl.minicheck.factcheck.create(claim=claim, context=contextnew) #chnge to old contxt if needed
        support_prob = factcheck_response.support_prob
        citations = perform_source_search(claim)
        
        print("citations : ",citations)
        # Return the result based on the support probability
        if support_prob > 0.5:  # Threshold for validity

            print("supported")
            # return jsonify({'valid': True, 'summary': "Claim is supported by the context."})
        else:
            print("unsupported")
            
            # return jsonify({'valid': False, 'summary': "Claim is not supported by the context."})
    except Exception as e:
        # Log any exceptions
        print("Error occurred:", str(e))
        return jsonify({'valid': False, 'message': 'An error occurred: ' + str(e)}), 500
    

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
    app.run(debug=True, host='0.0.0.0', port=5000)

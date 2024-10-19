from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from bespokelabs import BespokeLabs

app = Flask(__name__)
CORS(app)

# Initialize the Bespoke API client
bl = BespokeLabs(auth_token=os.environ.get("BESPOKE_API_KEY"))

def split_input(input_string):
    # Split the input based on "ChatGPT said:"
    parts = input_string.split("ChatGPT said:")
    
    if len(parts) < 2:
        raise ValueError("Input must contain 'ChatGPT said:' to separate context and claim.")
    
    context = parts[0].strip()  # Part before "ChatGPT said:"
    claim = parts[1].strip()    # Part after "ChatGPT said:"

    # If the claim starts with "ChatGPT", remove that part
    if claim.startswith("ChatGPT\n"):
        claim = claim.replace("ChatGPT\n", "", 1).strip()

    return context, claim


@app.route('/api/fetch-url', methods=['POST'])
def fetch_url():
    try:
        data = request.get_json()
        # Log the received data
        print("Received data:", data)

        url = data.get('url')  # This should contain both the context and claim
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

        # Call Bespoke API for fact-checking
        factcheck_response = bl.minicheck.factcheck.create(claim=claim, context=context)
        support_prob = factcheck_response.support_prob

        # Return the result based on the support probability
        if support_prob > 0.5:  # Threshold for validity
            return jsonify({'valid': True, 'summary': "Claim is supported by the context."})
        else:
            return jsonify({'valid': False, 'summary': "Claim is not supported by the context."})

    except Exception as e:
        # Log any exceptions
        print("Error occurred:", str(e))
        return jsonify({'valid': False, 'message': 'An error occurred: ' + str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

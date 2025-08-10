# app.py
# This is a Flask backend that uses the Google Gemini API for text generation.

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# IMPORTANT: You need a Gemini API key. Replace 'YOUR_GEMINI_API_KEY' with your actual key.
# You can get one for free at https://ai.google.dev/
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set. Please check your .env file.")

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# The Gemini API endpoint
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent"

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_input = data.get("message", "")

        print(f"[DEBUG] User input: {user_input}")

        if not user_input.strip():
            return jsonify({"response": "Please enter a message."}), 400

        # FIX: Create a more descriptive prompt to avoid safety filter issues.
        prompt_template = f"You are a helpful AI chatbot. Respond to the following user message: {user_input}"

        # Construct the payload for the Gemini API call
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": prompt_template}
                    ]
                }
            ],
            "generationConfig": {
                "maxOutputTokens": 150,
                "temperature": 0.7
            }
        }

        # Send the request to the Gemini API
        headers = {
            "Content-Type": "application/json"
        }
        
        # We need to add the API key as a query parameter for this endpoint.
        response = requests.post(f"{API_URL}?key={GEMINI_API_KEY}", json=payload, headers=headers)
        response.raise_for_status() # Raises an HTTPError if the status is 4xx or 5xx

        api_response_data = response.json()

        # The code now safely checks for the nested 'parts' key
        # to prevent the 'KeyError' when the API response is not a valid
        # text generation result (e.g., when it's blocked).
        if "candidates" in api_response_data and api_response_data["candidates"]:
            candidate = api_response_data["candidates"][0]
            if "content" in candidate and "parts" in candidate["content"]:
                bot_reply = candidate["content"]["parts"][0]["text"]
            else:
                # Handle cases where content is missing or blocked
                bot_reply = "I'm sorry, I cannot generate a response for that. The content may be inappropriate or violate safety policies."
        else:
            bot_reply = "Sorry, I couldn't generate a response."

        print(f"[DEBUG] Bot output: {bot_reply}")

        return jsonify({"response": bot_reply.strip()})

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Request failed: {e}")
        return jsonify({"response": f"Error: Request to API failed: {e}"}), 500
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[ERROR] {error_details}")
        return jsonify({"response": f"Error: {e}"}), 500

if __name__ == "__main__":
    app.run(debug=True)

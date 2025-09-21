from flask import Flask, render_template, request, jsonify
import requests
import os
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_ENDPOINT = "https://api.groq.ai/v1/chat/completions"  # correct endpoint

app = Flask(__name__)

def get_groq_response(user_message, mood=""):
    """
    Send user input to Groq chat model and get dynamic response.
    """
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    mood_text = f"The user is feeling {mood}. " if mood else ""
    system_message = {
        "role": "system",
        "content": f"You are a calm, empathetic, Zen-style AI. {mood_text} Respond naturally, encouragingly, and kindly."
    }

    user_msg = {
        "role": "user",
        "content": user_message if user_message else "User did not type anything."
    }

    payload = {
        "model": "llama3-chat-8b",
        "messages": [system_message, user_msg],
        "temperature": 0.7,
        "max_output_tokens": 150
    }

    try:
        response = requests.post(GROQ_ENDPOINT, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()
        # Extract AI reply from choices
        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"].strip()
        return "Hmm... I couldn’t generate a proper response."
    except Exception as e:
        return f"Sorry, I couldn’t connect to Groq: {str(e)}"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()
    mood = data.get("mood", "").strip()

    # Crisis detection
    if any(word in user_message.lower() for word in ["suicide", "help"]):
        return jsonify({
            "reply": "It seems you might be in crisis. Please contact a helpline immediately: 1-800-273-8255."
        })

    # Get AI reply from Groq
    reply = get_groq_response(user_message, mood)
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(debug=True, port=5005)

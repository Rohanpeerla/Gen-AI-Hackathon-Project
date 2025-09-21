from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load API key
load_dotenv()
GENAI_API_KEY = os.getenv("GENAI_API_KEY")

if not GENAI_API_KEY:
    raise ValueError("GENAI_API_KEY not found in .env file")

# Configure Gemini client
genai.configure(api_key=GENAI_API_KEY)

app = Flask(__name__)

def get_gemini_response(user_message, mood=""):
    """
    Send user input to Gemini 1.5 Flash via official SDK
    """
    try:
        mood_text = f"The user is feeling {mood}. " if mood else ""
        prompt_text = f"You are a calm, empathetic, Zen-style AI. {mood_text} Respond naturally, encouragingly, and kindly.\nUser: {user_message}"

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt_text)

        if response and response.candidates:
            return response.text.strip()
        return "Hmm... I couldn’t generate a proper response."
    except Exception as e:
        return f"Sorry, I couldn’t connect to Gemini: {str(e)}"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()
    mood = data.get("mood", "").strip()

    # If user clicked mood button only
    if not user_message and mood:
        reply = get_gemini_response("Respond to my current emotional state.", mood)
        return jsonify({"reply": reply})

    # Crisis detection
    if any(word in user_message.lower() for word in ["suicide", "help"]):
        return jsonify({
            "reply": "It seems you might be in crisis. Please contact a helpline immediately: 1-800-273-8255."
        })

    reply = get_gemini_response(user_message, mood)
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(debug=True, port=5005)

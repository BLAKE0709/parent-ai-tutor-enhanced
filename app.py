"""
Main Flask application for the Parent‑AI Tutor.

The app exposes two HTTP endpoints:

* GET '/' renders the chat interface.
* POST '/chat': accepts JSON data with a user message and the child’s age,
  forwards the request to the OpenAI API using a system prompt to adjust
  complexity, and returns the AI’s response as JSON.

Environment variable 'OPENAI_API_KEY' must be set to a valid OpenAI API key.
For development, copy '.env.example' to '.env' and fill in your key.
"""

from __future__ import annotations

import os
import logging
from typing import Dict, Any

from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import openai

# Load environment variables from .env file (if present)
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Retrieve the OpenAI API key from the environment.  Do not hardcode secrets.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)  # type: ignore[attr-defined]
    except AttributeError:
        openai.api_key = OPENAI_API_KEY
        client = None
else:
    client = None
    logger.warning(
        "OPENAI_API_KEY is not set. The app will run but chat requests will fail."
    )

# Define the Flask application
app = Flask(__name__)

def get_ai_response(message: str, age: int) -> str:
    """
    Send a prompt to OpenAI and return the assistant’s reply.
    Returns a fallback message if the API key is missing or the API call fails.
    """
    # If API key is missing, return fallback message
    if not OPENAI_API_KEY:
        return (
            "Sorry, I can’t generate an answer right now because the AI service "
            "is not configured. Please check your API key."
        )

    # Compose the system prompt with the child’s age
    system_prompt = (
        "You are an AI tutor helping parents explain artificial intelligence and technology "
        "concepts to their child. The child is {} years old. "
        "Speak directly to the parent and provide simple, age‑appropriate explanations, "
        "analogies and suggestions. Avoid jargon."
    ).format(age)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": message},
    ]

    try:
        if client:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=512,
            )
            content = response.choices[0].message.content
        else:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=512,
            )
            content = response["choices"][0]["message"]["content"]
        return content.strip()
    except Exception as e:
        logger.error(f"Error communicating with OpenAI: {e}")
        return "Sorry, the AI service is currently unavailable. Please try again later."

@app.route("/", methods=["GET"])
def index() -> str:
    """Render the chat interface."""
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat() -> (Any, int):
    """Handle chat POST requests.

    Expects JSON payload with keys:
        - message: str
        - age: int (child’s age)
    Returns JSON with either 'response' or 'error'.
    """
    data: Dict[str, Any] = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()
    age = data.get("age")

    # Validate inputs
    if not message:
        return jsonify({"error": "No message provided."}), 400
    try:
        age_int = int(age)
        if age_int < 1 or age_int > 18:
            return jsonify({"error": "Please enter an age between 1 and 18."}), 400
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid age provided."}), 400

    # Ask the AI
    reply = get_ai_response(message, age_int)
    return jsonify({"response": reply})

if __name__ == "__main__":
    # When running locally via `python app.py`, enable debug mode for convenience.
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)

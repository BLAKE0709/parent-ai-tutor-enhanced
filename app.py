"""
Updated Flask application for Parent‑AI Tutor with robust error handling.

This version improves the `get_ai_response` function by returning safe fallback
messages instead of raising exceptions when the API key is missing or when an
error occurs during the call to OpenAI.  It also removes references to
`openai.error` to be compatible with recent versions of the openai library.
"""

from __future__ import annotations

import os
import logging
from typing import Dict, Any

from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import openai

# Load environment variables from .env file if present
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Retrieve the OpenAI API key from the environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    try:
        # For openai>=1.0: create a client
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
    except AttributeError:
        # For older openai versions: set global api key
        openai.api_key = OPENAI_API_KEY
        client = None
else:
    client = None
    logger.warning(
        "OPENAI_API_KEY is not set. The app will run but chat requests will return a fallback message."
    )

# Initialise Flask app
app = Flask(__name__)


def get_ai_response(message: str, age: int) -> str:
    """Return the assistant’s reply or a fallback message on error.

    Args:
        message: The user’s input question.
        age: The child’s age, used to tailor the system prompt.

    Returns:
        A string containing the AI’s response or a fallback message.
    """
    # If the API key is missing, return fallback message
    if not OPENAI_API_KEY:
        return (
            "I’m sorry, but the AI service is not configured. Please set the OPENAI_API_KEY "
            "environment variable to enable responses."
        )
    # Compose the system prompt
    system_prompt = (
        "You are an AI tutor helping parents explain artificial intelligence and technology "
        "concepts to their child. The child is {} years old. Speak directly to the parent "
        "and provide simple, age‑appropriate explanations, analogies and suggestions. Avoid jargon."
    ).format(age)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": message.strip()},
    ]
    try:
        # Call OpenAI depending on version
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
    except Exception as exc:
        logger.error(f"AI request failed: {exc}")
        return "The AI service is currently unavailable or encountered an error. Please try again later."


@app.route("/")
def index() -> str:
    """Render the main chat page."""
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat() -> (Any, int):
    """Process a chat request and return JSON response."""
    data: Dict[str, Any] = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()
    age = data.get("age")
    if not message:
        return jsonify({"error": "No message provided."}), 400
    try:
        age_int = int(age)
        if age_int < 1 or age_int > 18:
            return jsonify({"error": "Please enter an age between 1 and 18."}), 400
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid age provided."}), 400
    reply = get_ai_response(message, age_int)
    return jsonify({"response": reply})


if __name__ == "__main__":
    # Use environment PORT if provided (Render sets PORT) else default 5000
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
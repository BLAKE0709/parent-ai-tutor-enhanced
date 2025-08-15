"""
Main Flask application for the Parent‑AI Tutor.

The app exposes two HTTP endpoints:

* GET `/` renders the chat interface.
* POST `/chat` accepts JSON data with a user message and the child’s age, 
  forwards the request to the OpenAI API using a system prompt to adjust 
  complexity, and returns the AI’s response as JSON.  

Environment variable `OPENAI_API_KEY` must be set to a valid OpenAI API key.  
For development, copy `.env.example` to `.env` and fill in your key.
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
    # For openai>=1.0, instantiate a client; for older versions, the global key is used
    try:
        # openai.OpenAI is available in v1.0+; fallback to setting api_key on module
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
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
    """Send a prompt to OpenAI and return the assistant’s reply.

    Args:
        message: The parent’s question or request.
        age: The child’s age to tailor the response.

    Returns:
        The assistant’s message content.

    Raises:
        ValueError: If the API key is missing or the API call fails.
    """
    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API key is not configured.")

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
            # For openai>=1.0: use the client to create a chat completion
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=512,
            )
            content = response.choices[0].message.content
        else:
            # For older openai versions: call ChatCompletion.create directly
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=512,
            )
            content = response["choices"][0]["message"]["content"]

        return content.strip()
    except openai.error.AuthenticationError as auth_err:
        logger.error(f"Authentication error: {auth_err}")
        raise ValueError("Invalid OpenAI API key. Please check your configuration.")
    except Exception as e:
        logger.error(f"Error communicating with OpenAI: {e}")
        raise ValueError("An error occurred while contacting OpenAI. Please try again later.")


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
    try:
        reply = get_ai_response(message, age_int)
        return jsonify({"response": reply})
    except ValueError as ve:
        # On expected errors (e.g. missing key), return 500
        return jsonify({"error": str(ve)}), 500


if __name__ == "__main__":
    # When running locally via `python app.py`, enable debug mode for convenience.
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)

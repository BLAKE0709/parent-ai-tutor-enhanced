<!-- 
  Architecture overview for the Parent‑AI Tutor. 
  Update this file whenever architectural decisions change.
-->

# Architecture

## Overview

The Parent‑AI Tutor consists of a lightweight Flask backend, a responsive front‑end styled with the Bootswatch **Lux** theme, and integration with OpenAI’s chat API. The app is container‑ and cloud‑friendly, with configuration via environment variables.

### Backend

- **Framework:** Flask
- **Entry point:** `app.py`
- **Endpoints:**
  - `GET /` renders the chat interface.
  - `POST /chat` accepts JSON `{message, age}` and returns a JSON response. The message is forwarded to the OpenAI API with a system prompt that tailors output to the specified age.
- **AI Integration:** OpenAI’s Chat Completion API is called through the `openai` Python library. We support both v0 and v1 clients by instantiating a client if available; otherwise we fall back to setting the global `openai.api_key`.
- **Error handling:** If the API key is missing or invalid, the endpoint returns a `500` error with a user‑friendly message. Input validation ensures an age between 1 and 18 is provided.

### Front‑end

- **Template:** `templates/index.html`
- **Styling:** Bootswatch **Lux** theme via CDN plus a custom `static/style.css`. The page uses the Inter font and a hero header, suggestions panel and chat container. JavaScript handles asynchronous calls to `/chat` and updates the UI.
- **UX enhancements:** Buttons to ask common questions, validation messages, and a disabled “Send” button while awaiting responses.

### Deployment

- **Procfile:** Specifies a Gunicorn command (`web: gunicorn app:app --workers=2 --threads=4 --timeout=120`) to serve the Flask app in production.
- **Requirements:** `requirements.txt` lists Flask, openai, python‑dotenv and gunicorn.
- **Environment:** The `OPENAI_API_KEY` must be set either in a `.env` file (for local development) or in the hosting provider’s configuration panel. No secrets are stored in the repository.
- **Hosting:** The app can be deployed on Render, Replit or any other platform that supports Python web services. A free Render service offers up to 750 instance hours per month【431169199308285†L268-L276】, which is sufficient for a single service.

### Future enhancements

- Persist chat history across requests.
- Prepopulate more suggested questions or topics.
- Offer learning plan generation for longer-term guidance.
- Add analytics and optional subscription features.

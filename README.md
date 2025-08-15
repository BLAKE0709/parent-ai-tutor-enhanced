# Parent‑AI Tutor

**Parent‑AI Tutor** is a polished minimal viable product that helps parents teach their children about artificial intelligence. It provides an age‑aware chat interface backed by OpenAI’s Chat Completion API. Parents specify their child’s age, ask questions and the AI responds with simple explanations and learning suggestions. The UI is styled with the elegant [Bootswatch Lux](https://bootswatch.com/lux/) theme and includes a hero header, suggestions panel and responsive chat bubbles.

## Why this idea?

Explaining complex technology to young learners is challenging. A guided chat experience not only delivers accurate answers but also builds trust. Focusing on parents avoids compliance risks associated with direct interaction with children and creates a pathway for premium educational tools.

## Features

- **Age‑smart chat:** The AI tailors its responses based on your child’s age input.
- **Beautiful interface:** The app uses the Lux Bootswatch theme, the Inter font and a hero header for a professional feel.
- **Suggested topics:** Quick‑start buttons encourage exploration of common AI topics.
- **Graceful error handling:** The app warns you when something goes wrong (e.g. missing API key).

## Installation

Prerequisites:

- Python 3.8+
- An OpenAI API key (obtain one from [OpenAI’s dashboard](https://platform.openai.com/account/api-keys)).

Steps:

```bash
git clone https://github.com/yourusername/parent-ai-tutor-enhanced.git
cd parent-ai-tutor-enhanced
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env  # then edit .env and set OPENAI_API_KEY
```

## Running locally

Start the development server with:

```bash
python app.py
```

Navigate to `http://localhost:5000/` to chat with the AI.

## Deployment

### Render

This repository includes a `Procfile` that uses Gunicorn to serve Flask in production. To deploy:

1. Create a new Web Service on [Render](https://render.com) and link this repository.
2. Set the **Build Command** to:

```bash
pip install -r requirements.txt
```

3. Set the **Start Command** to:

```bash
gunicorn app:app --workers=2 --threads=4 --timeout=120
```

4. Add an environment variable `OPENAI_API_KEY` in Render’s dashboard.
5. Deploy the service. On the free plan, Render provides 750 instance hours per month【431169199308285†L268-L276】, which is enough to run one web service continuously at no cost.

### Replit

1. Create a new Python (Flask) Repl and import this repository.
2. Add a secret `OPENAI_API_KEY` in the Secrets panel.
3. Replit automatically installs dependencies and runs the server. Click **Run** to launch the app.

## Contributing

Contributions are welcome! Please fork the repository, create a branch, make your changes and open a pull request.

## License

MIT License

## Acknowledgements

This project draws on the DeployApps tutorial for building a Flask‑based ChatGPT app【241949578249158†L160-L167】【241949578249158†L181-L239】 and adapts it to a parent‑centric educational tool.

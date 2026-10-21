# Smart Extractor & Chat Service

A Python API powered by LLMs to extract structured information from text and answer user questions.

## Features
- Structured text extraction: title, summary, keywords, and category
- LLM-powered chat with custom system instructions
- FastAPI endpoints with Swagger documentation
- Pydantic validation and error handling
- Automated tests using pytest and mocked responses
- Environment-based API configuration
- Streaming chat responses using SSE

## Tech Stack
Python, FastAPI, Pydantic, OpenRouter, OpenAI-compatible SDK, pytest, python-dotenv.

## Setup

```bash
git clone https://github.com/shoaib980-make/Smart-Extractor-Chat-Service
cd Smart-Extractor-Chat-Service/python_lab
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
```

Create a `.env` file:

```env
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_MODEL=openrouter/free
```

## Run the API

```bash
uvicorn main:app --reload
```

API documentation: http://127.0.0.1:8000/docs

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Welcome message |
| GET | `/health` | Health check |
| POST | `/extract` | Extract structured data |
| POST | `/chat` | Generate AI responses |
| POST | `/chat/stream` | Stream AI responses |

## Run Tests

```bash
python -m pytest -v
```

## Author

**Shoaib Asghar**  
BS Computer Science Graduate — Information Technology University (ITU), Lahore

- GitHub: https://github.com/shoaib980-make
- Repository: https://github.com/shoaib980-make/Smart-Extractor-Chat-Service
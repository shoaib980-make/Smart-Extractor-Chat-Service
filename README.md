
# Smart Extractor & Chat Service

An LLM-powered text extraction and API service built with Python, FastAPI, and OpenRouter. The project demonstrates reusable LLM integration, structured information extraction, error handling, and API testing.

## Features

- Integrates with LLMs through the OpenRouter API
- Reusable LLM service with configurable model selection
- Extracts structured information from text
- Returns title, summary, keywords, and category as JSON
- Validates model output and handles errors
- Provides REST API endpoints using FastAPI
- Includes automated tests using pytest
- Supports both Python and Node.js API experiments

## Tech Stack

- Python
- FastAPI
- Pydantic
- OpenRouter API
- OpenAI Python SDK
- Node.js
- pytest

## Project Structure

```text
Smart-Extractor-Chat-Service/
├── python_lab/
│   ├── llm_service.py
│   ├── structured_extractor.py
│   ├── main.py
│   ├── token_count.py
│   └── test_*.py
├── node_lab/
│   └── first_call.mjs
├── .gitignore
└── README.md
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/shoaib980-make/Smart-Extractor-Chat-Service.git
cd Smart-Extractor-Chat-Service
```

### 2. Set up the Python environment

```bash
cd python_lab
python -m venv .venv
```

Activate it on Windows Git Bash:

```bash
source .venv/Scripts/activate
```

Install the dependencies used by the project:

```bash
pip install openai python-dotenv tiktoken fastapi uvicorn pytest httpx
```

### 3. Configure your API key

Create a `.env` file inside `python_lab/`:

```env
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_MODEL=nvidia/nemotron-3-super-120b-a12b:free
```

Replace the placeholder with your own OpenRouter API key. Never commit your `.env` file or publish your API key.

### 4. Run the API

From the `python_lab/` directory:

```bash
uvicorn main:app --reload
```

The API will be available at:

- Home: http://127.0.0.1:8000/
- Health check: http://127.0.0.1:8000/health
- Interactive API documentation: http://127.0.0.1:8000/docs

## API Endpoint

### POST `/extract`

Extract structured information from input text.

Example request:

```json
{
  "text": "FastAPI is a Python framework for building APIs. It supports type hints and automatic API documentation."
}
```

Example response:

```json
{
  "title": "Introduction to FastAPI",
  "summary": "FastAPI is a Python framework for building APIs with type hints and automatic documentation.",
  "keywords": ["FastAPI", "Python", "APIs", "type hints"],
  "category": "Technology"
}
```

The actual extracted values depend on the model response.

## Run Tests

From the `python_lab/` directory:

```bash
python -m pytest -v
```

## Learning Goals

This project explores:

- LLM API integration
- Prompt engineering
- Token counting
- Structured data extraction
- Input and output validation
- API error handling
- FastAPI development
- Automated testing

## Author

**Shoaib Asghar**  
BS Computer Science Graduate — Information Technology University (ITU), Lahore

GitHub: https://github.com/shoaib980-make

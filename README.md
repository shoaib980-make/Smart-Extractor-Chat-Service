
# Smart Extractor & Chat Service

A Python API that uses Large Language Models (LLMs) to extract structured information from text and answer user questions.

## Features

- **Structured text extraction** into a title, summary, keywords, and category
- **LLM-powered chat** with customizable system instructions
- **FastAPI** endpoints with automatic Swagger documentation
- **Pydantic** request and response validation
- **Error handling** for invalid inputs and LLM service failures
- **Automated tests** using pytest and mocked LLM responses
- **Environment-based configuration** for API credentials

## Tech Stack

- Python
- FastAPI
- Pydantic
- OpenAI-compatible SDK
- OpenRouter
- pytest
- python-dotenv

## Project Structure

```text
Smart Extractor & Chat Service/
├── python_lab/
│   ├── main.py
│   ├── llm_service.py
│   ├── structured_extractor.py
│   ├── evaluate_extractor.py
│   ├── evaluation_dataset.json
│   ├── evaluation_results.json
│   ├── prompts/
│   │   └── templates.json
│   ├── test_api.py
│   ├── test_extractor.py
│   ├── test_error_handling.py
│   ├── test_llm_service.py
│   ├── test_prompt_retry.py
│   ├── test_structured_output.py
│   ├── token_count.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   └── package.json
├── node_lab/
│   ├── first_call.mjs
│   └── package.json
├── PROMPT_ENGINEERING_REPORT.md
├── BAD_PROMPTS.md
├── DEPLOYMENT.md
├── .gitignore
└── README.md
```

## Setup

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd "Smart Extractor & Chat Service"
```

### 2. Create and activate a virtual environment

```bash
cd python_lab
python -m venv .venv
```

Git Bash on Windows:

```bash
source ".venv/Scripts/activate"
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file inside `python_lab/`:

```env
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_MODEL=openrouter/free
```

Use your own API key. Never commit `.env` to GitHub.

## Run the API

From inside `python_lab/`:

```bash
uvicorn main:app --reload
```

Open the interactive API documentation:

http://127.0.0.1:8000/docs

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | API welcome message |
| GET | `/health` | Health check |
| POST | `/extract` | Extract structured information |
| POST | `/chat` | Generate an LLM response |
| POST | `/chat/stream` | Stream an LLM response via SSE |

## Example Requests

### Extract information

POST `/extract`

```json
{
  "text": "Python is a programming language used in web development, automation, and artificial intelligence."
}
```

Expected response shape:

```json
{
  "title": "Python Programming Language",
  "summary": "Python is used for web development, automation, and AI.",
  "keywords": ["Python", "Web Development", "Automation", "AI"],
  "category": "Technology"
}
```

The exact extracted content may vary depending on the LLM response.

### Chat

POST `/chat`

```json
{
  "message": "Explain FastAPI in simple words.",
  "system_instruction": "You are a helpful programming tutor."
}
```

Expected response shape:

```json
{
  "reply": "FastAPI is a Python framework for building APIs..."
}
```

The reply will vary depending on the model.

## Run Tests

From inside `python_lab/`:

```bash
python -m pytest -v
```

Tests that mock the LLM service can run without making real model requests.

## Security Notes

- Keep API keys in environment variables.
- Do not commit `.env` files.
- Validate incoming request data.
- Avoid returning internal exception details to API users.
- Use appropriate request limits and logging.

## Future Improvements

- Add rate limiting and authentication.
- Add persistent chat history.
- Support PDF and document uploads.
- Add Docker deployment.
- Add CI with GitHub Actions.

## License

Add a license if you intend to distribute this project publicly.


## Author

**Shoaib Asghar**  
BS Computer Science Graduate — Information Technology University (ITU), Lahore

- GitHub: https://github.com/shoaib980-make
- Project Repository: https://github.com/shoaib980-make/Smart-Extractor-Chat-Service
```

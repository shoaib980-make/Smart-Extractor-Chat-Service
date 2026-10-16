
# Smart Extractor & Chat Service

An LLM-powered text extraction and chat API built with **Python, FastAPI, and OpenRouter**. This project demonstrates reusable LLM integration, structured information extraction, customizable chat instructions, input validation, error handling, logging, and automated API testing.

## Features

- Integrates with large language models through the OpenRouter API.
- Provides a reusable LLM service with configurable model selection.
- Extracts structured information from text.
- Returns extracted titles, summaries, keywords, and categories as JSON.
- Supports an AI chat endpoint with customizable system instructions.
- Validates incoming requests using Pydantic.
- Parses and validates structured LLM output.
- Handles API connection errors, rate limits, and unexpected failures.
- Includes application logging for debugging and monitoring.
- Provides interactive API documentation through Swagger UI.
- Includes automated API tests using pytest and mocked LLM responses.
- Contains Python and Node.js API experiments.

## Tech Stack

- **Language:** Python, JavaScript (Node.js)
- **API Framework:** FastAPI
- **Data Validation:** Pydantic
- **LLM Integration:** OpenRouter API, OpenAI Python SDK
- **Environment Configuration:** python-dotenv
- **Token Counting:** tiktoken
- **Testing:** pytest, HTTPX
- **API Server:** Uvicorn

## Project Structure

```text
Smart-Extractor-Chat-Service/
├── python_lab/
│   ├── .env
│   ├── llm_service.py
│   ├── structured_extractor.py
│   ├── main.py
│   ├── token_count.py
│   ├── first_call.py
│   ├── openrouter_call.py
│   ├── test_llm_service.py
│   ├── test_structured_output.py
│   ├── test_extractor.py
│   ├── test_error_handling.py
│   └── test_api.py
├── node_lab/
│   ├── .env
│   └── first_call.mjs
├── .gitignore
└── README.md
```

> The `.env` files contain local configuration and should never be committed to Git.

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/shoaib980-make/Smart-Extractor-Chat-Service.git
cd Smart-Extractor-Chat-Service
```

### 2. Set Up the Python Environment

Navigate to the Python project:

```bash
cd python_lab
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows Git Bash:

```bash
source .venv/Scripts/activate
```

Install the dependencies:

```bash
python -m pip install openai python-dotenv tiktoken fastapi uvicorn pytest httpx
```

### 3. Configure Environment Variables

Create a `.env` file inside `python_lab/`:

```env
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_MODEL=nvidia/nemotron-3-super-120b-a12b:free
```

Replace `your_api_key_here` with your own OpenRouter API key.

**Security:** Never commit your `.env` file or expose your API key in source code, screenshots, logs, or public repositories.

### 4. Run the API

From the `python_lab/` directory, run:

```bash
uvicorn main:app --reload
```

The API will start at `http://127.0.0.1:8000`.

### 5. Explore the API

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Confirms that the API is running |
| `/health` | GET | Returns the health status |
| `/extract` | POST | Extracts structured information from text |
| `/chat` | POST | Generates an AI response using a prompt and system instructions |
| `/docs` | GET | Opens interactive Swagger API documentation |

Open these URLs in your browser:

- Home: http://127.0.0.1:8000/
- Health check: http://127.0.0.1:8000/health
- Swagger UI: http://127.0.0.1:8000/docs

## API Usage

### 1. Extract Structured Information

**Endpoint:** `POST /extract`

Extract a title, summary, keywords, and category from input text.

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
  "keywords": [
    "FastAPI",
    "Python",
    "APIs",
    "type hints"
  ],
  "category": "Technology"
}
```

The actual extracted values depend on the LLM response.

### 2. Chat with the LLM

**Endpoint:** `POST /chat`

Send a message to the LLM and optionally customize its behavior with a system instruction.

Example request:

```json
{
  "message": "Explain Python functions in simple terms.",
  "system_instruction": "You are a patient Python tutor. Explain concepts with simple examples."
}
```

Example response:

```json
{
  "reply": "A Python function is a reusable block of code that performs a specific task..."
}
```

The actual response depends on the selected model.

If `system_instruction` is omitted, the API uses its default instruction.

## Error Handling and Validation

The API includes input validation and error handling to improve reliability.

- **200 OK:** Request completed successfully.
- **422 Unprocessable Entity:** Request data is missing, invalid, or fails validation.
- **502 Bad Gateway:** An upstream LLM service fails or returns unusable data.
- **500 Internal Server Error:** An unexpected server-side error occurs.

Empty or whitespace-only text is rejected, and unexpected errors are logged for debugging.

## Run Tests

From the `python_lab/` directory, execute:

```bash
python -m pytest -v
```

The test suite covers API endpoints, input validation, successful responses, LLM failures, and unexpected errors.

LLM calls are mocked in API tests where appropriate, allowing tests to run without making real model requests.

## Learning Goals

This project explores:

- LLM API integration
- Prompt engineering and system instructions
- Token counting
- Structured information extraction
- JSON parsing and output validation
- Environment variable management
- FastAPI routing and request validation
- Pydantic data models
- Exception handling and logging
- Automated testing with pytest
- Mocking external API dependencies
- REST API development

## Future Improvements

- Add authentication and rate limiting.
- Support file uploads and document extraction.
- Add conversation history and persistent storage.
- Introduce response caching.
- Add Docker-based deployment.
- Deploy the API to a cloud platform.

## Author

**Shoaib Asghar**  
BS Computer Science Graduate — Information Technology University (ITU), Lahore

- GitHub: https://github.com/shoaib980-make
- Project Repository: https://github.com/shoaib980-make/Smart-Extractor-Chat-Service
```


from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator

from structured_extractor import extract_information
from llm_service import generate_response

import logging

logger = logging.getLogger(__name__)
app = FastAPI(title="Smart Extractor API")


class ExtractionRequest(BaseModel):
    text: str = Field(min_length=1)

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Text cannot contain only whitespace.")
        return value

class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    system_instruction: str = Field(
        default="You are a helpful assistant. Answer clearly and accurately.",
        min_length=1,
        max_length=500,
    )

    @field_validator("message", "system_instruction")
    @classmethod
    def validate_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Field cannot contain only whitespace.")
        return value
    
class ExtractionResponse(BaseModel):
    title: str
    summary: str
    keywords: list[str]
    category: str

class ChatResponse(BaseModel):
    reply: str

@app.get("/")
def home():
    return {"message": "Smart Extractor API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/extract", response_model=ExtractionResponse)
def extract(request: ExtractionRequest):
    try:
        return extract_information(request.text)

    except ValueError:
        logger.warning("Extraction returned invalid data.")
        raise HTTPException(
            status_code=502,
            detail="The extraction service returned invalid data.",
        ) from None

    except RuntimeError:
        logger.warning("Extraction service operation failed.")
        raise HTTPException(
            status_code=502,
            detail="The extraction service is temporarily unavailable.",
        ) from None

    except Exception:
        logger.exception("Unexpected error during text extraction.")
        raise HTTPException(
            status_code=500,
            detail="An unexpected server error occurred.",
        ) from None

    

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        reply = generate_response(
            prompt=request.message,
            system_instruction=request.system_instruction,
            max_tokens=800,
        )

        return ChatResponse(reply=reply)

    except RuntimeError:
        logger.warning("Chat service operation failed.")
        raise HTTPException(
            status_code=502,
            detail="The chat service is temporarily unavailable.",
        ) from None

    except Exception:
        logger.exception("Unexpected error during chat.")
        raise HTTPException(
            status_code=500,
            detail="An unexpected server error occurred.",
        ) from None

def test_chat_custom_system_instruction():
    instruction = "You are a patient Python tutor."

    with patch(
        "main.generate_response",
        return_value="A function is reusable code.",
    ) as mock_generate:
        response = client.post(
            "/chat",
            json={
                "message": "What is a function?",
                "system_instruction": instruction,
            },
        )

    assert response.status_code == 200
    assert response.json()["reply"] == (
        "A function is reusable code."
    )

    mock_generate.assert_called_once_with(
        prompt="What is a function?",
        system_instruction=instruction,
        max_tokens=800,
    )

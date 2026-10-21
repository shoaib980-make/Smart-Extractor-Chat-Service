import json
import logging
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, field_validator

from llm_service import generate_response, stream_response
from structured_extractor import (
    PROMPTS,
    ExtractionResult,
    extract_information,
    parse_extraction_json,
)

logger = logging.getLogger(__name__)
app = FastAPI(title="Smart Extractor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ExtractionRequest(BaseModel):
    text: str = Field(min_length=1, max_length=10000)

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Text cannot contain only whitespace.")
        return value


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=5000)

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


def strip_safety_prefix(text: str) -> str:
    """Removes model safety prefix artifacts like 'User Safety: safe'."""
    return re.sub(r"^(User\s+Safety:\s*safe\s*)+", "", text, flags=re.IGNORECASE)


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


@app.post("/extract/stream")
def extract_stream(request: ExtractionRequest):
    def generate():
        try:
            template = PROMPTS["extract"]
            prompt = template["template"].replace("{{text}}", request.text)
            accumulated = []

            for piece in stream_response(
                prompt=prompt,
                system_instruction=template["system"],
                max_tokens=3000,
            ):
                accumulated.append(piece)
                yield f"data: {json.dumps({'chunk': piece})}\n\n"

            full_text = "".join(accumulated)
            try:
                data = parse_extraction_json(full_text)
                result = ExtractionResult.model_validate(data)
                yield f"data: {json.dumps({'done': True, 'result': result.model_dump()})}\n\n"
            except Exception:
                logger.warning("Streaming extraction JSON validation failed; retrying with feedback fallback.")
                fallback_result = extract_information(request.text)
                yield f"data: {json.dumps({'done': True, 'result': fallback_result})}\n\n"

        except Exception:
            logger.exception("Streaming extraction failed")
            yield f"data: {json.dumps({'error': 'The extraction service returned invalid data or is unavailable.'})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        reply = generate_response(
            prompt=request.message,
            system_instruction=request.system_instruction,
            max_tokens=3000,
        )
        cleaned_reply = strip_safety_prefix(reply)
        return ChatResponse(reply=cleaned_reply)

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


@app.post("/chat/stream")
def chat_stream(request: ChatRequest):
    def generate():
        try:
            started = False
            for piece in stream_response(
                prompt=request.message,
                system_instruction=request.system_instruction,
                max_tokens=3000,
            ):
                if not started:
                    cleaned_piece = strip_safety_prefix(piece)
                    if not cleaned_piece:
                        continue
                    started = True
                    yield f"data: {json.dumps({'chunk': cleaned_piece})}\n\n"
                else:
                    yield f"data: {json.dumps({'chunk': piece})}\n\n"

            yield f"data: {json.dumps({'done': True})}\n\n"

        except Exception:
            logger.exception("Streaming chat failed")
            yield f"data: {json.dumps({'error': 'Chat service temporarily unavailable.'})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
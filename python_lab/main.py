
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from structured_extractor import extract_information
import logging

logger = logging.getLogger(__name__)
app = FastAPI(title="Smart Extractor API")


class ExtractionRequest(BaseModel):
    text: str = Field(min_length=1)


class ExtractionResponse(BaseModel):
    title: str
    summary: str
    keywords: list[str]
    category: str


@app.get("/")
def home():
    return {"message": "Smart Extractor API is running"}


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

    
@app.get("/health")
def health_check():
    return {"status": "healthy"}
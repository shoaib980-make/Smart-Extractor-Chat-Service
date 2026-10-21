import json
import logging
import re
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from llm_service import generate_response

logger = logging.getLogger(__name__)

TEMPLATE_FILE = Path(__file__).parent / "prompts" / "templates.json"

with TEMPLATE_FILE.open("r", encoding="utf-8") as file:
    PROMPTS = json.load(file)


class ExtractionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    keywords: list[str]
    category: str = Field(min_length=1)


def parse_extraction_json(raw: str) -> dict:
    """Safely parse JSON from raw LLM output, removing safety headers, think tags, and markdown blocks."""
    cleaned = raw.strip()

    # 1. Strip <think>...</think> blocks
    cleaned = re.sub(r"<think>[\s\S]*?</think>", "", cleaned, flags=re.IGNORECASE).strip()

    # 2. Strip safety headers like "User Safety: safe"
    cleaned = re.sub(r"^(User\s+Safety:\s*safe\s*)+", "", cleaned, flags=re.IGNORECASE).strip()

    # 3. Extract JSON inside markdown code blocks ```json ... ``` or ``` ... ```
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned, flags=re.IGNORECASE)
    if match:
        candidate = match.group(1).strip()
        try:
            return json.loads(candidate)
        except Exception:
            pass

    # 4. Extract outer { ... } if preamble or postamble exists
    first_brace = cleaned.find("{")
    last_brace = cleaned.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        candidate = cleaned[first_brace : last_brace + 1]
        try:
            return json.loads(candidate)
        except Exception:
            pass

    # 5. Fallback to direct json.loads (which will raise JSONDecodeError if invalid)
    return json.loads(cleaned)


def extract_information(text: str) -> dict:
    """Extract structured information, validate it, and retry invalid output."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Input text must be a non-empty string.")

    template = PROMPTS["extract"]
    prompt = template["template"].replace("{{text}}", text)
    feedback = ""

    for attempt in range(1, 4):
        current_prompt = prompt

        if feedback:
            current_prompt += (
                "\n\nYour previous response was invalid. Fix these issues:\n"
                f"{feedback}\nReturn a corrected JSON object only."
            )

        response = generate_response(
            prompt=current_prompt,
            system_instruction=template["system"],
            max_tokens=3000,
        )

        try:
            data = parse_extraction_json(response)
            result = ExtractionResult.model_validate(data)
            logger.info("Extraction succeeded on attempt %s.", attempt)
            return result.model_dump()

        except json.JSONDecodeError:
            feedback = "The response was not valid JSON."
        except ValidationError as error:
            feedback = str(error)
        except (TypeError, ValueError) as error:
            feedback = str(error)

        logger.warning("Invalid extraction output on attempt %s of 3.", attempt)

    raise ValueError(
        "Extraction failed after 3 attempts because the model "
        "did not return valid structured data."
    )

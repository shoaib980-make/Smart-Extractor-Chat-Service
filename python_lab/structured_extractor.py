
import json
from llm_service import generate_response


def extract_information(text: str) -> dict:
    
    """Extract and validate structured information from text."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Input text must be a non-empty string.")
    
    prompt = f"""
Extract information from the text below.

Return ONLY a valid JSON object with these fields:
- title: string
- summary: string
- keywords: list of strings
- category: string

Do not include Markdown or explanations.

Text:
{text}
"""

    response = generate_response(
        prompt=prompt,
        system_instruction=(
            "You are an information extraction assistant. "
            "Return only a valid JSON object."
        ),
        max_tokens=800,
    )

    try:
        data = json.loads(response)
    except json.JSONDecodeError as error:
        raise ValueError("The model did not return valid JSON.") from error

    expected_types = {
        "title": str,
        "summary": str,
        "keywords": list,
        "category": str,
    }

    for field, expected_type in expected_types.items():
        if field not in data:
            raise ValueError(f"Missing required field: {field}")

        if not isinstance(data[field], expected_type):
            raise ValueError(
                f"Field '{field}' must be a {expected_type.__name__}."
            )

    if not all(isinstance(word, str) for word in data["keywords"]):
        raise ValueError("Every keyword must be a string.")

    return data

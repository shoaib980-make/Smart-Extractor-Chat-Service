
import json
from llm_service import generate_response

text = """
OpenAI released a new AI tool that helps developers build
applications faster. It supports Python and JavaScript.
The tool is designed to improve developer productivity.
"""

prompt = f"""
Extract information from the text below.

Return ONLY a valid JSON object with these four fields:
- title: a short title as a string
- summary: a short summary as a string
- keywords: a list of strings
- category: a short category as a string

Do not include Markdown code fences or any text outside the JSON.

Text:
{text}
"""

response = generate_response(
    prompt=prompt,
    system_instruction=(
        "You are an information extraction assistant. "
        "Extract information from the user's text. "
        "Return a valid JSON object with title, summary, "
        "keywords, and category. "
        "The keywords field must be an array of strings. "
        "Do not return safety labels, explanations, or Markdown."
    ),
    max_tokens=800,
)

try:
    data = json.loads(response)

    # Define the expected structure
    required_fields = {
        "title": str,
        "summary": str,
        "keywords": list,
        "category": str,
    }

    # Check required fields and their data types
    for field, expected_type in required_fields.items():
        if field not in data:
            raise ValueError(f"Missing field: {field}")

        if not isinstance(data[field], expected_type):
            raise ValueError(
                f"Field '{field}' must be a "
                f"{expected_type.__name__}"
            )

    # Check that every keyword is a string
    if not all(
        isinstance(keyword, str)
        for keyword in data["keywords"]
    ):
        raise ValueError("Every keyword must be a string.")

    # Check that text fields are not empty
    for field in ("title", "summary", "category"):
        if not data[field].strip():
            raise ValueError(f"Field '{field}' cannot be empty.")

    print("\nValidated structured information:")
    print(json.dumps(data, indent=2, ensure_ascii=False))

except (json.JSONDecodeError, ValueError) as error:
    print("Could not process the model's response:", error)
    print("Raw response:", response)


bad_response = "User Safety: safe"

try:
    json.loads(bad_response)
except json.JSONDecodeError as error:
    print("\nTest passed: invalid JSON was caught.")
    print("Error:", error)
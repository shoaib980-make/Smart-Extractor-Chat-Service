
from unittest.mock import patch
from structured_extractor import extract_information

sample_text = "FastAPI is a Python framework for building APIs."

# Simulate an LLM returning invalid JSON.
with patch(
    "structured_extractor.generate_response",
    return_value="This is not JSON",
):
    try:
        extract_information(sample_text)
    except ValueError as error:
        print("Error handling passed:", error)
    else:
        print("Test failed: invalid JSON was not rejected.")

# Simulate valid JSON with an incorrect field type.
bad_json = """
{
    "title": "FastAPI",
    "summary": "A Python framework",
    "keywords": "Python, APIs",
    "category": "Technology"
}
"""

with patch(
    "structured_extractor.generate_response",
    return_value=bad_json,
):
    try:
        extract_information(sample_text)
    except ValueError as error:
        print("Schema validation passed:", error)
    else:
        print("Test failed: incorrect field type was accepted.")

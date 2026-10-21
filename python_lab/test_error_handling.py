from unittest.mock import patch
import pytest
from structured_extractor import extract_information

sample_text = "FastAPI is a Python framework for building APIs."


def test_invalid_json_handling():
    # Simulate an LLM returning invalid JSON.
    with patch(
        "structured_extractor.generate_response",
        return_value="This is not JSON",
    ):
        with pytest.raises(ValueError) as excinfo:
            extract_information(sample_text)
        assert "did not return valid structured data" in str(excinfo.value)


def test_incorrect_field_type_handling():
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
        with pytest.raises(ValueError) as excinfo:
            extract_information(sample_text)
        assert "did not return valid structured data" in str(excinfo.value)


if __name__ == "__main__":
    test_invalid_json_handling()
    print("Error handling passed: invalid JSON was rejected.")
    test_incorrect_field_type_handling()
    print("Schema validation passed: incorrect field type was rejected.")

from unittest.mock import patch

import pytest

from structured_extractor import extract_information


VALID_JSON = (
    '{"title":"FastAPI","summary":"A Python web framework.",'
    '"keywords":["Python","API"],"category":"Technology"}'
)


def test_valid_json_succeeds_first_attempt():
    with patch(
        "structured_extractor.generate_response",
        return_value=VALID_JSON,
    ) as mock_llm:
        result = extract_information("FastAPI is a Python web framework.")

    assert result["title"] == "FastAPI"
    assert result["keywords"] == ["Python", "API"]
    assert mock_llm.call_count == 1


def test_invalid_json_is_retried():
    with patch(
        "structured_extractor.generate_response",
        side_effect=["not JSON", VALID_JSON],
    ) as mock_llm:
        result = extract_information("FastAPI is a Python web framework.")

    assert result["title"] == "FastAPI"
    assert mock_llm.call_count == 2
    assert "previous response was invalid" in mock_llm.call_args_list[1].kwargs["prompt"]


def test_retries_exhausted():
    with patch(
        "structured_extractor.generate_response",
        return_value="not JSON",
    ) as mock_llm:
        with pytest.raises(ValueError, match="after 3 attempts"):
            extract_information("Some source text.")

    assert mock_llm.call_count == 3


def test_empty_text_is_rejected():
    with pytest.raises(ValueError, match="non-empty"):
        extract_information("   ")

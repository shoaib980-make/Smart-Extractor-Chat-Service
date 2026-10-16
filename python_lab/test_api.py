
from fastapi.testclient import TestClient
from unittest.mock import patch

from main import app

client = TestClient(app)


def test_home_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Smart Extractor API is running"
    }


def test_extract_success():
    fake_result = {
        "title": "FastAPI",
        "summary": "A Python framework for building APIs.",
        "keywords": ["Python", "APIs"],
        "category": "Software Development",
    }

    with patch(
        "main.extract_information",
        return_value=fake_result,
    ) as mock_extract:
        response = client.post(
            "/extract",
            json={
                "text": "FastAPI is a Python framework."
            },
        )

    assert response.status_code == 200
    assert response.json() == fake_result
    mock_extract.assert_called_once_with(
        "FastAPI is a Python framework."
    )


def test_extract_empty_text():
    response = client.post(
        "/extract",
        json={"text": ""},
    )

    assert response.status_code == 422

def test_extract_llm_failure():
    with patch(
        "main.extract_information",
        side_effect=RuntimeError(
            "Could not connect to the API."
        ),
    ):
        response = client.post(
            "/extract",
            json={"text": "FastAPI is a Python framework."},
        )

    assert response.status_code == 502
    assert response.json() == {
        "detail": "The extraction service is temporarily unavailable."
    }

def test_unexpected_error_is_logged():
    with patch(
        "main.extract_information",
        side_effect=Exception("Internal test failure"),
    ):
        with patch("main.logger.exception") as mock_logger:
            response = client.post(
                "/extract",
                json={"text": "Test input"},
            )

    assert response.status_code == 500
    assert response.json() == {
        "detail": "An unexpected server error occurred."
    }
    mock_logger.assert_called_once_with(
        "Unexpected error during text extraction."
    )
def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
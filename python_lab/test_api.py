
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

def test_extract_whitespace_only_text():
    response = client.post(
        "/extract",
        json={"text": "   "},
    )

    assert response.status_code == 422

def test_chat_success():
    with patch(
        "main.generate_response",
        return_value="FastAPI is a Python framework for APIs.",
    ) as mock_generate:
        response = client.post(
            "/chat",
            json={"message": "What is FastAPI?"},
        )

    assert response.status_code == 200
    assert response.json() == {
        "reply": "FastAPI is a Python framework for APIs."
    }
    mock_generate.assert_called_once()

def test_chat_empty_message():
    response = client.post(
        "/chat",
        json={"message": ""},
    )

    assert response.status_code == 422

def test_chat_llm_failure():
    with patch(
        "main.generate_response",
        side_effect=RuntimeError("API unavailable"),
    ):
        response = client.post(
            "/chat",
            json={"message": "Hello"},
        )

    assert response.status_code == 502
    assert response.json() == {
        "detail": "The chat service is temporarily unavailable."
    }

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
    assert response.json()["reply"] == "A function is reusable code."
    mock_generate.assert_called_once_with(
        prompt="What is a function?",
        system_instruction=instruction,
        max_tokens=3000,
    )


def test_chat_whitespace_only_message():
    response = client.post(
        "/chat",
        json={"message": "   "},
    )

    assert response.status_code == 422


def test_chat_whitespace_only_system_instruction():
    response = client.post(
        "/chat",
        json={
            "message": "Explain Python.",
            "system_instruction": "   ",
        },
    )

    assert response.status_code == 422
def test_extract_text_too_long():
    response = client.post(
        "/extract",
        json={"text": "a" * 10001},
    )

    assert response.status_code == 422


def test_chat_message_too_long():
    response = client.post(
        "/chat",
        json={"message": "a" * 5001},
    )

    assert response.status_code == 422

def test_chat_unexpected_error_is_logged(caplog):
    with patch(
        "main.generate_response",
        side_effect=Exception("Sensitive internal detail"),
    ):
        with caplog.at_level("ERROR", logger="main"):
            response = client.post(
                "/chat",
                json={"message": "Explain Python."},
            )

    assert response.status_code == 500
    assert response.json() == {
        "detail": "An unexpected server error occurred."
    }
    assert "Unexpected error during chat." in caplog.text
    assert "Sensitive internal detail" not in response.json()["detail"]


def test_chat_stream_success():
    with patch(
        "main.stream_response",
        return_value=["FastAPI ", "is ", "fast."],
    ) as mock_stream:
        response = client.post(
            "/chat/stream",
            json={
                "message": "What is FastAPI?",
                "system_instruction": "Be concise.",
            },
        )

    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    text = response.text
    assert '{"chunk": "FastAPI "}' in text
    assert '{"chunk": "is "}' in text
    assert '{"chunk": "fast."}' in text
    assert '{"done": true}' in text
    mock_stream.assert_called_once_with(
        prompt="What is FastAPI?",
        system_instruction="Be concise.",
        max_tokens=3000,
    )


def test_chat_stream_failure():
    with patch(
        "main.stream_response",
        side_effect=RuntimeError("Stream failure"),
    ):
        response = client.post(
            "/chat/stream",
            json={"message": "Hello"},
        )

    assert response.status_code == 200
    assert '{"error": "Chat service temporarily unavailable."}' in response.text


def test_extract_stream_success():
    fake_json = '{"title":"FastAPI","summary":"A Python framework.","keywords":["Python","API"],"category":"Tech"}'
    with patch(
        "main.stream_response",
        return_value=[fake_json],
    ):
        response = client.post(
            "/extract/stream",
            json={"text": "FastAPI is a Python framework."},
        )

    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    text = response.text
    assert '"done": true' in text
    assert '"FastAPI"' in text
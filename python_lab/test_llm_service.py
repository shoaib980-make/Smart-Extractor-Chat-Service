from unittest.mock import patch, MagicMock

from llm_service import generate_response


def test_generate_response_success():
    choice = MagicMock()
    choice.message.content = "RAG retrieves relevant information and uses it to generate an answer."
    choice.finish_reason = "stop"

    mock_response = MagicMock()
    mock_response.choices = [choice]
    mock_response.model = "test-model"
    mock_response.usage = None

    with patch(
        "llm_service.client.chat.completions.create",
        return_value=mock_response,
    ) as mock_create:
        answer = generate_response(
            prompt="Explain RAG.",
            system_instruction="You are a helpful AI tutor.",
            max_tokens=3000,
        )

    assert answer == choice.message.content
    mock_create.assert_called_once()

    call_kwargs = mock_create.call_args.kwargs
    assert call_kwargs["model"]
    assert call_kwargs["max_tokens"] == 3000
    assert call_kwargs["messages"][0]["content"] == (
        "You are a helpful AI tutor."
    )
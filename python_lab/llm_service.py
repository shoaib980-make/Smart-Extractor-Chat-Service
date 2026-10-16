import os

from dotenv import load_dotenv
from openai import OpenAI, APIConnectionError, APIStatusError, RateLimitError

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
model = os.getenv("OPENROUTER_MODEL", "openrouter/free")

if not api_key:
    raise RuntimeError("OPENROUTER_API_KEY is missing from .env")

client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1",
    timeout=30.0,
    max_retries=2,
)

def generate_response(
    prompt: str,
    system_instruction: str = "You are a helpful assistant.",
    max_tokens: int = 800,
) -> str:
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
            
        )

        choice = response.choices[0]
        content = choice.message.content

        print("Model used:", response.model)
        print("Finish reason:", choice.finish_reason)

        if not content or not content.strip():
            raise RuntimeError(
                "The model returned no readable text. "
                "Try the request again or select another model."
            )

        if choice.finish_reason == "length":
            print("Warning: The response may be incomplete.")

        return content

    except RateLimitError:
        raise RuntimeError(
            "The model is rate-limited. Try again later."
        ) from None

    except APIConnectionError:
        raise RuntimeError(
            "Could not connect to the API. Check your internet connection."
        ) from None

    except APIStatusError as error:
        raise RuntimeError(
            f"The API returned an error: HTTP {error.status_code}"
        ) from None
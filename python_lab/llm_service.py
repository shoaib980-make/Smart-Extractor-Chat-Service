import os
import logging
from dotenv import load_dotenv
from openai import OpenAI, APIConnectionError, APIStatusError, RateLimitError
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

from pathlib import Path

_env_file = Path(__file__).resolve().parent / ".env"
if _env_file.exists():
    load_dotenv(dotenv_path=_env_file)
load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
model = os.getenv("OPENROUTER_MODEL", "openrouter/free")

client = OpenAI(
    api_key=api_key or "not-set",
    base_url="https://openrouter.ai/api/v1",
    timeout=30.0,
    max_retries=2,
)

def log_usage(response, model):
    usage = getattr(response, "usage", None)

    if not usage:
        logger.info("Token usage unavailable for model: %s", model)
        return

    prompt_tokens = getattr(usage, "prompt_tokens", 0) or 0
    completion_tokens = getattr(usage, "completion_tokens", 0) or 0
    total_tokens = getattr(
        usage,
        "total_tokens",
        prompt_tokens + completion_tokens
    ) or 0

    # OpenRouter may provide the actual request cost.
    actual_cost = getattr(usage, "cost", None)

    if actual_cost is not None:
        cost_message = f"Actual cost: ${float(actual_cost):.8f}"
    else:
        input_rate = float(
            os.getenv("OPENROUTER_INPUT_PRICE_PER_MILLION", "0")
        )
        output_rate = float(
            os.getenv("OPENROUTER_OUTPUT_PRICE_PER_MILLION", "0")
        )

        if input_rate > 0 or output_rate > 0:
            estimated_cost = (
                prompt_tokens * input_rate
                + completion_tokens * output_rate
            ) / 1_000_000
            cost_message = f"Estimated cost: ${estimated_cost:.8f}"
        else:
            cost_message = "Cost unavailable: pricing not configured"

    logger.info(
        "Model: %s | Input tokens: %s | Output tokens: %s "
        "| Total tokens: %s | %s",
        model,
        prompt_tokens,
        completion_tokens,
        total_tokens,
        cost_message,
    )

def generate_response(
    prompt: str,
    system_instruction: str = "You are a helpful assistant.",
    max_tokens: int = 3000,
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
        log_usage(response, model)
        choice = response.choices[0] 
        content = choice.message.content

        logger.info("LLM request completed. Model: %s", response.model)

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
        logger.warning("LLM request was rate-limited.")
        raise RuntimeError(
            "The model is rate-limited. Try again later."
        ) from None

    except APIConnectionError:
        logger.warning("Could not connect to the LLM API.")
        raise RuntimeError(
            "Could not connect to the API. Check your internet connection."
        ) from None

    except APIStatusError as error:
        logger.error("LLM API returned HTTP %s.", error.status_code)
        raise RuntimeError(
            f"The API returned an error: HTTP {error.status_code}"
        ) from None




def stream_response(prompt, system_instruction, max_tokens=3000):
    try:
        stream = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
            stream=True,
        )

        for chunk in stream:
            if not chunk.choices:
                continue

            choice = chunk.choices[0]
            content = choice.delta.content

            if content:
                yield content

            if choice.finish_reason:
                logger.info(
                    "Stream finished. Reason: %s",
                    choice.finish_reason,
                )

    except Exception:
        logger.exception("Error while streaming model response")
        raise

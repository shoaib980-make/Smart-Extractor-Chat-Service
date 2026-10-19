import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    raise RuntimeError("OPENROUTER_API_KEY is missing from .env")

client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1",
)

response = client.chat.completions.create(
    model="openrouter/free",
    messages=[
        {
            "role": "system",
            "content": "You are a helpful programming tutor. Answer the user's question directly in plain text."
        },
        {
            "role": "user",
            "content": "In two simple sentences, explain what an API is."
        }
    ],
        max_tokens=3000,
    )

message = response.choices[0].message

print("Response:", message.content)
print("Finish reason:", response.choices[0].finish_reason)
print("Token usage:", response.usage)

from llm_service import generate_response

answer = generate_response(
    prompt="Explain RAG in three simple sentences.",
    system_instruction=(
        "You are an AI/ML tutor. "
        "Explain technical concepts clearly."
    ),
    max_tokens=800,
)

print("LLM Response:")
print(answer)

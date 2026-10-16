
import "dotenv/config";
import OpenAI from "openai";

const apiKey = process.env.OPENROUTER_API_KEY;

if (!apiKey) {
  throw new Error("OPENROUTER_API_KEY is missing from .env");
}

const client = new OpenAI({
  apiKey,
  baseURL: "https://openrouter.ai/api/v1",
});

async function main() {
  const response = await client.chat.completions.create({
    model: "openrouter/free",
    messages: [
      {
        role: "system",
        content:
          "You are a helpful programming tutor. Answer clearly in plain text.",
      },
      {
        role: "user",
        content: "Explain an API in two simple sentences.",
      },
    ],
    max_tokens: 300,
  });

  console.log("Response:", response.choices[0].message.content);
  console.log("Finish reason:", response.choices[0].finish_reason);
  console.log("Token usage:", response.usage);
}

main().catch((error) => {
  console.error("API request failed:", error.message);
  process.exitCode = 1;
});

import os
from openai import AsyncOpenAI
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

load_dotenv("backend/.env")

# Fetch API key from environment
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    logger.warning("OPENROUTER_API_KEY is not set in the environment.")

# We use the official OpenAI SDK but pointed to OpenRouter
# The default model "deepseek/deepseek-chat" resolves to DeepSeek V3 on OpenRouter.
MODEL_NAME = os.environ.get("LLM_MODEL", "deepseek/deepseek-chat")

# Initialize the AsyncOpenAI client
client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

async def generate_chat_completion(messages: list[dict], temperature: float = 0.0) -> str:
    """
    Calls OpenRouter to generate a response using the DeepSeek model.
    """
    try:
        response = await client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "http://localhost:3000", # Required by OpenRouter
                "X-Title": "RAG Document Intelligence System", # Optional but recommended
            },
            model=MODEL_NAME,
            messages=messages,
            temperature=temperature,
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        logger.error(f"OpenRouter API call failed: {e}")
        raise

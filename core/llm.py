import os
import time
from dotenv import load_dotenv
from core.config import LLM_MODEL, LLM_TEMPERATURE, LLM_MAX_RETRIES

load_dotenv()


def get_llm():
    # Lazy import — langchain_groq transitively pulls in torch on import,
    # so we defer it until the LLM is first needed (not on app startup).
    from langchain_groq import ChatGroq
    return ChatGroq(
        model=LLM_MODEL,
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=LLM_TEMPERATURE,
    )


def call_llm_safe(llm, prompt: str, max_retries: int = LLM_MAX_RETRIES):
    """Invoke the LLM with exponential-backoff retry (1 s → 2 s → 4 s)."""
    last_err = None
    for attempt in range(max_retries):
        try:
            return llm.invoke(prompt)
        except Exception as e:
            last_err = e
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
    raise last_err

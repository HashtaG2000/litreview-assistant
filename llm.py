import os
import time
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()


def get_llm():
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.3
    )


def call_llm_safe(llm, prompt, max_retries=3):
    """
    Fix 5: Invoke the LLM with exponential-backoff retry.

    Handles transient Groq errors (rate limits, 5xx, timeouts) so the app
    doesn't crash on a single API hiccup.  Delays: 1 s → 2 s → 4 s.

    Raises the last exception if all attempts fail — callers should catch and
    show a user-friendly st.error message.
    """
    last_err = None
    for attempt in range(max_retries):
        try:
            return llm.invoke(prompt)
        except Exception as e:
            last_err = e
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)   # 1 s, 2 s, 4 s
    raise last_err


if __name__ == "__main__":
    llm = get_llm()
    response = call_llm_safe(llm, "What is machine learning in one sentence?")
    print(response.content)

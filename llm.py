import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

def get_llm():
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.3
    )

if __name__ == "__main__":
    llm = get_llm()
    response = llm.invoke("What is machine learning in one sentence?")
    print(response.content)

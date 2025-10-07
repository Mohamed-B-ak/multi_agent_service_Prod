"""
RAG Query Script with Pinecone (v4 SDK) + OpenAI
------------------------------------------------
- Retrieves user-specific data from Pinecone
- Generates context-grounded answers
pip install openai pinecone python-dotenv numpy
"""

import os
import time
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone

# ------------------------------------------------------------
# 1. Load environment
# ------------------------------------------------------------
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX", "rag-multiuser")

if not OPENAI_API_KEY or not PINECONE_API_KEY:
    raise ValueError("❌ Missing API keys in .env file")

# Initialize clients
client = OpenAI()


# ------------------------------------------------------------
# 2. Define retrieval function (user-specific)

# ------------------------------------------------------------
# 3. Generate grounded response
# ------------------------------------------------------------
def respond_to_user_with_rag(prompt: str, user_email: str) -> str:
    """
    Retrieves user-specific context and generates an answer.
    """
    start = time.time()
    context = retrieve_context(prompt, user_email)

    messages = [
        {"role": "system", "content": f"Use this context to answer accurately:\n{context}"},
        {"role": "user", "content": prompt},
    ]

    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )

    print(f"⏱️ Response generated in {time.time() - start:.2f}s")
    return resp.choices[0].message.content

# ------------------------------------------------------------
# 4. Interactive mode
# ------------------------------------------------------------
if __name__ == "__main__":
    print("🧠 Multi-User RAG Query Mode\n")
    user_email = input("📧 Enter user email (namespace): ").strip()

    while True:
        user_input = input("\n💬 Ask a question (or type 'exit'): ")
        if user_input.lower() in ["exit", "quit"]:
            print("👋 Goodbye!")
            break

        answer = respond_to_user_with_rag(user_input, user_email)
        print("\n🤖", answer)

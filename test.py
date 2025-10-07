import os
from pymongo import MongoClient
from dotenv import load_dotenv
from pinecone import Pinecone
import re 

# ------------------------------------------------------------
# 1. Load environment
# ------------------------------------------------------------
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX", "rag-multiuser")
from dotenv import load_dotenv
import os

load_dotenv()

print(os.getenv("DB_NAME"))
print(os.getenv("MONGO_DB_URI"))
client = MongoClient(os.getenv("MONGO_DB_URI"))
db = client[os.getenv("DB_NAME")]
collection = db["whatsappmessages"]


def retrieve_context(query: str, user_email: str, k: int = 2) -> str:
    """
    Retrieve top-k relevant chunks for a query from:
    - The user's personal namespace (user_email)
    - The shared system namespace ("system@diyadah-ai.com")
    Both results are merged and sorted by similarity.
    """
    pc = Pinecone(api_key=PINECONE_API_KEY)

    # Connect to Pinecone index
    index = pc.Index(INDEX_NAME)
    print(f"✅ Connected to Pinecone index '{INDEX_NAME}'\n")
    emb = client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    ).data[0].embedding

    # Query user namespace
    user_results = index.query(
        namespace=user_email,
        vector=emb,
        top_k=k,
        include_metadata=True
    )

    # Query system (shared) namespace
    system_results = index.query(
        namespace="system@diyadah-ai.com",
        vector=emb,
        top_k=k,
        include_metadata=True
    )

    # Combine both result sets
    all_matches = []
    if "matches" in user_results:
        all_matches.extend(user_results["matches"])
    if "matches" in system_results:
        all_matches.extend(system_results["matches"])

    # Sort all results by similarity (descending)
    all_matches = sorted(all_matches, key=lambda x: x.get("score", 0), reverse=True)

    # Limit to top-k total
    top_contexts = [m["metadata"]["text"] for m in all_matches[:k]]

    if not top_contexts:
        return "No relevant data found."

    return "\n".join(top_contexts)

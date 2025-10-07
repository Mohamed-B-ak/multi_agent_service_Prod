from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os, time
from pymongo import MongoClient
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
import tiktoken
from dotenv import load_dotenv

# ------------------------------------------------------------
# 1. Setup
# ------------------------------------------------------------
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
MONGO_URI = os.getenv("MONGO_DB_URI")
INDEX_NAME = os.getenv("PINECONE_INDEX", "rag-multiuser")

if not all([OPENAI_API_KEY, PINECONE_API_KEY, MONGO_URI]):
    raise ValueError("❌ Missing required environment variables.")

# Initialize clients
client = OpenAI()
pc = Pinecone(api_key=PINECONE_API_KEY)
mongo_client = MongoClient(MONGO_URI)
db = mongo_client.get_database()
collection = db["knowledgebases"]

# Ensure Pinecone index exists
if INDEX_NAME not in [i["name"] for i in pc.list_indexes()]:
    print(f"📦 Creating Pinecone index '{INDEX_NAME}'...")
    pc.create_index(
        name=INDEX_NAME,
        dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )
    time.sleep(5)

index = pc.Index(INDEX_NAME)
print("✅ Pinecone connected and ready.\n")

# ------------------------------------------------------------
# 2. Router setup
# ------------------------------------------------------------
router = APIRouter()



# ------------------------------------------------------------
# 4. Helper functions
# ------------------------------------------------------------
def chunk_text(text: str, max_tokens: int = 500) -> list[str]:
    """Split long text into smaller chunks by token count."""
    enc = tiktoken.get_encoding("cl100k_base")
    tokens = enc.encode(text)
    chunks = []
    for i in range(0, len(tokens), max_tokens):
        chunk = enc.decode(tokens[i:i + max_tokens])
        chunks.append(chunk)
    return chunks

def index_user_data(user_email: str, content: str):
    """Embed text chunks and store in Pinecone."""
    namespace = user_email
    chunks = chunk_text(content)
    vectors = []

    for i, chunk in enumerate(chunks):
        emb = client.embeddings.create(
            model="text-embedding-3-small",
            input=chunk
        ).data[0].embedding
        vectors.append({
            "id": f"{namespace}-{i}-{int(time.time())}",
            "values": emb,
            "metadata": {"text": chunk}
        })

    index.upsert(vectors=vectors, namespace=namespace)
    print(f"✅ Indexed {len(chunks)} chunks for {namespace}.")
    return len(chunks)

import os
from crewai import LLM
from pymongo import MongoClient
import os

from dotenv import load_dotenv
import os

load_dotenv()

print(os.getenv("DB_NAME"))
print(os.getenv("MONGO_DB_URI"))
client = MongoClient(os.getenv("MONGO_DB_URI"))
db = client[os.getenv("DB_NAME")]
collection = db["whatsappmessages"]


def get_llm():
    """
    Initialize the LLM (Large Language Model) with a predefined model and API key.
    """
    return LLM(
        model="gpt-4o",
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.1,
        max_tokens=500,

    )


def get_last_messages(to_number: str, limit: int = 4):
    """
    Fetch the last `limit` WhatsApp messages for a given customer number.
    Ordered from newest → oldest.
    """
    cursor = (
        collection.find({"to_number": to_number})
        .sort("time", -1)  # -1 = descending
        .limit(limit)
    )
    return list(cursor)

print(get_last_messages("+21653844063"))

import json

def save_message(redis_client, user_email: str, role: str, content: str, limit: int = 20):

    key = f"chat:{user_email}"
    entry = {"role": role, "content": content}
    redis_client.rpush(key, json.dumps(entry))   # push new message
    redis_client.ltrim(key, -limit, -1)          # keep last N messages

def get_messages(redis_client, user_email: str, limit: int = 20):

    
    key = f"chat:{user_email}"
    messages = redis_client.lrange(key, -limit, -1)
    return [json.loads(m) for m in messages]

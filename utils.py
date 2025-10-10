import os
from crewai import LLM
from pymongo import MongoClient
import os
import os
import time
from dotenv import load_dotenv
from openai import OpenAI
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
#client = MongoClient(os.getenv("MONGO_DB_URI"))
#db = client[os.getenv("DB_NAME")]
#collection = db["whatsappmessages"]


def get_llm():
    """
    Initialize the LLM (Large Language Model) with a predefined model and API key.
    """
    return LLM(
        model="gpt-3.5-turbo",
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.1,
        max_tokens=500,

    )


def get_last_messages(to_number: str, db, limit: int = 4):
    """
    Fetch the last `limit` WhatsApp messages for a given customer number.
    Ordered from newest → oldest.
    """
    collection = db["whatsappmessages"]
    cursor = (
        collection.find({"to_number": to_number})
        .sort("time", -1)  # -1 = descending
        .limit(limit)
    )
    return list(cursor)


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



from openai import OpenAI



def respond_to_user(prompt: str, user_email: str, userlanguage: str, dialect: str, tone: str, urgency: str, index, openai_client) -> str:
    """
    Retrieves user-specific context and generates an answer.
    """
    start = time.time()
    context = retrieve_context(prompt, user_email, index, openai_client)

    messages = [
        {"role": "system", "content": f"Use this context to answer accurately:\n\n the response should respect : \n\n the user language {userlanguage} \n the dialect {dialect} \n the tone {tone} \n the urgency {urgency} \n\n  {context}"},
        {"role": "user", "content": prompt},
    ]

    resp = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    print(f"⏱️ Response generated in {time.time() - start:.2f}s")
    return resp.choices[0].message.content


def check_required_data(prompt: str, context: list, openai_client) -> dict:
    system_prompt = """
                    You are an intelligent assistant. Your task is to verify whether the user's latest request contains enough required information, considering both the current request and prior conversation context.
                    You must always return JSON only in this format:

                    {
                        "need_details": "yes" or "no",
                        "message": "short message in the user's language"
                    }

                    Rules:

                    - Add Customer:
                    Must include BOTH "customer name" AND (at least "phone" OR "email").

                    - Delete Customer:
                    Must include at least ONE identifier: "name" OR "phone" OR "email".
                    - Prepare Campaign: 
                    Must include 
                        * Channel → whatsapp OR email (if not exist in Conversation history)
                        * Campaign type → welcome, marketing, reminder, offer, discount, etc... (if not exist in Conversation history)
                    - Send Campaign:
                    Must include:
                        * Channel → whatsapp OR email (if not exist in Conversation history)
                        * Campaign type → welcome, marketing, reminder, offer, discount, etc... (if not exist in Conversation history)
                        * Target → single customer OR bulk (if not exist in Conversation history)

                    - General Questions (e.g., "كيف يمكن للنظام مساعدتي", "What can you do?"):
                    → These do NOT require details.
                    → Return need_details = "no" with a helpful message describing the system capabilities.

                    Validation Rules:
                    - If required fields are missing for action requests, return need_details = "yes" with a short message asking for missing info.
                    - If request is a general question or enough fields are provided, return need_details = "no".
                    - Always write the message in the same language as the user's latest prompt.
                    - Only return JSON.
                    """


    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Conversation:\n{context}\n\nLatest request: {prompt}"}
        ],
        temperature=0
    )

    print(response)
    raw_output = response.choices[0].message.content.strip()
    print(raw_output)
    # 🔹 Remove Markdown code fences if present
    if raw_output.startswith("```"):
        raw_output = re.sub(r"^```(?:json)?|```$", "", raw_output, flags=re.MULTILINE).strip()

    try:
        return json.loads(raw_output)
    except json.JSONDecodeError:
        return {
            "need_details": "yes",
            "message": "⚠️ Failed to parse response. Please try again."
        }


def retrieve_context(query: str, user_email: str, index, openai_client, k: int = 2) -> str:
    """
    Retrieve top-k relevant chunks for a query from:
    - The user's personal namespace (user_email)
    - The shared system namespace ("system@diyadah-ai.com")
    Both results are merged and sorted by similarity.
    """

    print(f"✅ Connected to Pinecone index '{INDEX_NAME}'\n")
    emb = openai_client.embeddings.create(
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



def standard_result_parser(result):
    if isinstance(result, dict) and result.get("status") == "success":
        print("✅ Task completed successfully, stopping agent loop.")
        return result.get("message", result)
    elif isinstance(result, dict) and result.get("status") == "error":
        print("❌ Error detected, stopping loop.")
        return f"حدث خطأ: {result['message']}"
    return result

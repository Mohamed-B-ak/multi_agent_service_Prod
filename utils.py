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
        model="gpt-3.5-turbo",
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



from openai import OpenAI

# Initialize client
client = OpenAI()

def respond_to_user(prompt: str, context: str) -> str:
    """
    Call OpenAI API with a user prompt and context, return the response.
    
    Args:
        prompt (str): The user's input.
        context (str): Background context to guide the response.
    
    Returns:
        str: The model's reply.
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # or "gpt-4o-mini" for cheaper/faster
        messages=[
            {"role": "system", "content": f"Context: {context}"},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content


from openai import OpenAI
import re
client = OpenAI()

def check_required_data(prompt: str, context: list) -> dict:
    system_prompt = """
                    You are an intelligent assistant. Your job is to check whether the user's request contains enough required information or not.
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


    response = client.chat.completions.create(
        model="gpt-4o",
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
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

client = OpenAI()

def check_required_data(prompt: str, context: list) -> dict:
    """
    Use OpenAI API to decide if user prompt + context contains enough information.
    Returns JSON { need_details: "yes"/"no", message: str }
    
    Args:
        prompt (str): Latest user input.
        context (list): Conversation history [{'role': 'system'|'user', 'content': str}, ...].
        required_fields (list): List of required fields.
    """
    required = ["customer_name", "customer_phone", "customer_email", "campaign_content", "channel_type"]
    system_prompt = """
    أنت مساعد ذكي وظيفتك أن تتحقق إذا كان طلب المستخدم مكتمل البيانات أم لا.
    يجب أن تعيد دائمًا JSON فقط بهذا الشكل:
    {
        "need_details": "yes" أو "no",
        "message": "رسالة قصيرة"
    }

    القواعد:
    - إذا لم يتوفر كل المطلوب (مثل اسم العميل، رقم الهاتف، البريد الإلكتروني، نوع الحملة، نوع القناة)
      أرجع need_details = "yes" مع رسالة مثل "من فضلك أعطني مزيد من التفاصيل".
    - إذا كانت كل البيانات موجودة ضمن الحوار أو الـ context،
      أرجع need_details = "no" مع رسالة تأكيد.
    - لا تُرجع أي شيء غير الـ JSON.
    """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",   # أو "gpt-4o-mini"
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"الحوار:\n{context}\n\nآخر طلب: {prompt}\n\nالحقول المطلوبة: {required}"}
        ],
        temperature=0
    )
    return json.loads(response.choices[0].message.content)


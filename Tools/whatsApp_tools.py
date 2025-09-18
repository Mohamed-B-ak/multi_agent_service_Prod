# tools.py

import os
from crewai.tools import BaseTool
from pymongo import MongoClient
from whatsapp_client_python.whatsapp_client import WhatsAppClient


class WhatsAppTool(BaseTool):
    name: str = "WhatsApp Tool"
    description: str = (
        "Use for sending WhatsApp messages. Args: to_number(str), message(str). "
        "Fetches WhatsApp credentials dynamically from MongoDB based on user_email."
    )

    # ✅ declare user_email as a Pydantic field (like MailerSendTool)
    user_email: str

    async def _arun(self, to_number: str, message: str) -> str:
        """Async execution entrypoint for CrewAI tools"""

        # --- Step 1: Fetch WhatsApp credentials ---
        try:
            client = MongoClient(os.getenv("MONGO_DB_URI"))
            db = client[os.getenv("DB_NAME")]
            collection = db["usercredentials"]

            user_doc = collection.find_one({"userEmail": self.user_email})
            if not user_doc:
                return f"❌ No credentials found for {self.user_email}"

            whatsapp_doc = user_doc.get("whatsapp", {})
            session_name = whatsapp_doc.get("sessionName")
            api_key = whatsapp_doc.get("apiKey")

            if not session_name or not api_key:
                return f"❌ WhatsApp credentials are missing for {self.user_email}"

        except Exception as e:
            return f"❌ Error fetching WhatsApp credentials: {str(e)}"

        # --- Step 2: Send message via WhatsApp client ---
        try:
            async with WhatsAppClient(session_name=session_name, api_key=api_key) as client:
                success = await client.send_message(to_number, message)

            if success:
                return f"✅ WhatsApp message successfully sent to {to_number}: {message[:80]}"
            else:
                return f"❌ Failed to send WhatsApp message to {to_number}: {message[:80]}"

        except Exception as e:
            return f"❌ WhatsApp error: {str(e)}"

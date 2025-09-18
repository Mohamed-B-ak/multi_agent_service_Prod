# tools.py

import os
import asyncio
from crewai.tools import BaseTool
from pymongo import MongoClient
from whatsapp_client_python.whatsapp_client import WhatsAppClient


class WhatsAppTool(BaseTool):
    name: str = "WhatsApp Tool"
    description: str = (
        "Use for sending WhatsApp messages. Args: to_number(str), message(str). "
        "Fetches WhatsApp credentials dynamically from MongoDB based on user_email."
    )

    user_email: str

    # --- required by BaseTool (sync) ---
    def _run(self, to_number: str, message: str) -> str:
        """Fallback sync version: submits to running loop if present"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # submit task to running loop
                future = asyncio.run_coroutine_threadsafe(
                    self._arun(to_number, message), loop
                )
                return future.result()
            else:
                # no loop running → safe to block
                return loop.run_until_complete(self._arun(to_number, message))
        except Exception as e:
            return f"❌ WhatsApp error (sync fallback): {str(e)}"

    # --- async version (CrewAI will prefer this if supported) ---
    async def _arun(self, to_number: str, message: str) -> str:
        # Step 1: Fetch WhatsApp credentials
        try:
            mongo_client = MongoClient(os.getenv("MONGO_DB_URI"))
            db = mongo_client[os.getenv("DB_NAME")]
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

        # Step 2: Send WhatsApp message
        try:
            async with WhatsAppClient(session_name=session_name, api_key=api_key) as client:
                success = await client.send_message(to_number, message)

            if success:
                return f"✅ WhatsApp message successfully sent to {to_number}: {message[:80]}"
            else:
                return f"❌ Failed to send WhatsApp message to {to_number}: {message[:80]}"

        except Exception as e:
            return f"❌ WhatsApp error: {str(e)}"

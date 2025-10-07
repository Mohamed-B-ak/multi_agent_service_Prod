# whatsApp_tools.py
import os
import asyncio
import platform
import inspect
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from crewai.tools import BaseTool
from pymongo import MongoClient
from whatsapp_client_python.whatsapp_client import WhatsAppClient

# ✅ Apply nest_asyncio only on Windows (local dev)
if platform.system() == "Windows":
    import nest_asyncio
    nest_asyncio.apply()

# Shared thread executor for running async in sync contexts
_EXECUTOR = ThreadPoolExecutor(max_workers=1)

class WhatsAppTool(BaseTool):
    name: str = "WhatsApp Tool"
    description: str = (
        "Use for sending WhatsApp messages. Args: to_number(str), message(str). "
        "Fetches WhatsApp credentials dynamically from MongoDB based on user_email."
    )

    # ✅ declare user_email as a Pydantic field
    user_email: str

    # --- SYNC entrypoint (CrewAI may call this) ---
    def _run(self, to_number: str, message: str) -> str:
        """Sync fallback: runs async code in a background thread"""
        try:
            future = _EXECUTOR.submit(lambda: asyncio.run(self._arun(to_number, message)))
            result = future.result()
            # ✅ Pass through if _arun() already returns structured dict
            if isinstance(result, dict):
                return result

            # ✅ Wrap plain string responses
            return {"status": "success", "message": str(result)}

        except Exception as e:
            return {"status": "error", "message": f"❌ WhatsApp error (sync): {e}"}

    # --- ASYNC entrypoint (preferred when supported) ---
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
                result = client.send_message(to_number, message)

                # ✅ Handle both coroutine and bool return types
                if inspect.isawaitable(result):
                    success = await result
                else:
                    success = result

            if success:
                try:
                    clean_number = to_number.replace("@c.us", "")  # Remove @c.us
                    if not clean_number.startswith("+"):
                        clean_number = "+" + clean_number  # Add + if missing
                    emails_collection = db["whatsappmessages"]  
            
                    new_message = {"assistant": message}

                    # Vérifier si une conversation existe déjà
                    existing_conversation = emails_collection.find_one({
                        "user_email": self.user_email,
                        "to_number": clean_number
                    })

                    if existing_conversation:
                        # Mettre à jour la conversation existante
                        emails_collection.update_one(
                            {"_id": existing_conversation["_id"]},
                            {
                                "$push": {"messages": new_message},
                                "$set": {"time": datetime.utcnow()}
                            }
                        )
                    else:
                        # Créer une nouvelle conversation
                        emails_collection.insert_one({
                            "user_email": self.user_email,
                            "to_number": clean_number,
                            "time": datetime.utcnow(),
                            "messages": [new_message]
                        })
                    return {
                        "status": "success",
                        "to_number": clean_number,
                        "message": f"✅ WhatsApp message successfully sent to {clean_number}.",
                        "preview": message[:80]
                    }

                except Exception as e:
                    return {
                        "status": "success",
                        "to_number": clean_number,
                        "message": f"✅ Message sent to {clean_number}, but saving failed: {e}",
                        "preview": message[:80]
                    }

            else:
                return {
                    "status": "error",
                    "to_number": clean_number,
                    "message": f"❌ Failed to send WhatsApp message to {clean_number}.",
                    "preview": message[:80]
                }

        except Exception as e:
            return {"status": "error", "message": f"❌ WhatsApp error: {e}"}
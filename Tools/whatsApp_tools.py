# whatsApp_tools.py
import os
import asyncio
import platform
import inspect
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from crewai.tools import BaseTool
from pymongo import MongoClient
from whatsapp_client_python.whatsapp_client import WhatsAppClient

# ✅ Apply nest_asyncio only on Windows (for local dev)
if platform.system() == "Windows":
    import nest_asyncio
    nest_asyncio.apply()

# Shared thread executor for running async code in sync contexts
_EXECUTOR = ThreadPoolExecutor(max_workers=1)


class WhatsAppTool(BaseTool):
    # ✅ Tool name must match exactly what you reference in agent goals/backstory
    name: str = "WhatsAppTool"
    description: str = (
        "Send WhatsApp messages to a recipient. "
        "Args: to_number(str), message(str). "
        "Fetches WhatsApp credentials dynamically from MongoDB based on user_email."
    )

    # ✅ Required user context
    user_email: str

    # --- SYNC entrypoint (CrewAI often calls this) ---
    def _run(self, to_number: str, message: str) -> str:
        """Runs async code in a background thread (CrewAI compatibility)."""
        try:
            print(f"[TOOL] WhatsAppTool called (sync) → sending to {to_number}")
            future = _EXECUTOR.submit(lambda: asyncio.run(self._arun(to_number, message)))
            result = future.result()

            # ✅ Ensure plain text return for CrewAI
            if isinstance(result, dict):
                return result.get("message", str(result))

            return str(result)

        except Exception as e:
            return f"❌ WhatsApp error (sync): {e}"

    # --- ASYNC entrypoint (preferred if supported by environment) ---
    async def _arun(self, to_number: str, message: str) -> str:
        """Actual WhatsApp sending logic (async)."""

        # Step 1: Fetch WhatsApp credentials
        try:
            mongo_client = MongoClient(os.getenv("MONGO_DB_URI"))
            db = mongo_client[os.getenv("DB_NAME")]
            collection = db["usercredentials"]

            user_doc = collection.find_one({"userEmail": self.user_email})
            if not user_doc:
                return f"❌ No WhatsApp credentials found for {self.user_email}"

            whatsapp_doc = user_doc.get("whatsapp", {})
            session_name = whatsapp_doc.get("sessionName")
            api_key = whatsapp_doc.get("apiKey")

            if not session_name or not api_key:
                return f"❌ WhatsApp credentials missing for {self.user_email}"

        except Exception as e:
            return f"❌ Error fetching WhatsApp credentials: {e}"

        # Step 2: Send WhatsApp message
        try:
            print(f"[TOOL] Sending WhatsApp message via session '{session_name}' to {to_number}")
            async with WhatsAppClient(session_name=session_name, api_key=api_key) as client:
                # ✅ Always await send_message in case it's coroutine-based
                result = client.send_message(to_number, message)
                if inspect.isawaitable(result):
                    success = await result
                else:
                    success = result

            clean_number = to_number.replace("@c.us", "")
            if not clean_number.startswith("+"):
                clean_number = "+" + clean_number

            if success:
                try:
                    # ✅ Save conversation history in MongoDB
                    messages_col = db["whatsappmessages"]
                    new_message = {"assistant": message}
                    existing_conversation = messages_col.find_one({
                        "user_email": self.user_email,
                        "to_number": clean_number
                    })

                    if existing_conversation:
                        messages_col.update_one(
                            {"_id": existing_conversation["_id"]},
                            {
                                "$push": {"messages": new_message},
                                "$set": {"time": datetime.utcnow()}
                            }
                        )
                    else:
                        messages_col.insert_one({
                            "user_email": self.user_email,
                            "to_number": clean_number,
                            "time": datetime.utcnow(),
                            "messages": [new_message]
                        })

                    print(f"[TOOL] ✅ WhatsApp message sent successfully to {clean_number}")
                    return f"✅ WhatsApp message successfully sent to {clean_number}."

                except Exception as e:
                    print(f"[TOOL] ⚠️ Message sent but saving failed: {e}")
                    return f"✅ Message sent to {clean_number}, but saving failed: {e}"

            else:
                print(f"[TOOL] ❌ WhatsApp send failed for {clean_number}")
                return f"❌ Failed to send WhatsApp message to {clean_number}."

        except Exception as e:
            return f"❌ WhatsApp error: {e}"


class WhatsAppBulkSenderTool(BaseTool):
    name: str = "WhatsAppBulkSenderTool"
    description: str = (
        "Send WhatsApp messages in bulk to multiple recipients. "
        "Args: recipients numbers(List[str]), message(str or List[str]). "
        "Supports personalized or same message broadcast. "
        "Fetches WhatsApp credentials dynamically from MongoDB based on user_email."
    )

    user_email: str

    # --- SYNC ENTRYPOINT (for CrewAI compatibility) ---
    def _run(self, recipients: List[str], message: Any) -> str:
        """Run the async bulk sender in a thread executor (sync-friendly)."""
        try:
            print(f"[TOOL] WhatsAppBulkSenderTool → sending to {len(recipients)} recipients")
            future = _EXECUTOR.submit(lambda: asyncio.run(self._arun(recipients, message)))
            result = future.result()

            if isinstance(result, dict):
                return result.get("summary", str(result))
            return str(result)

        except Exception as e:
            return f"❌ WhatsApp bulk error (sync): {e}"

    # --- ASYNC ENTRYPOINT (preferred if environment supports async) ---
    async def _arun(self, recipients: List[str], message: Any) -> Dict[str, Any]:
        """
        Sends messages to multiple WhatsApp numbers.
        Supports list of messages for per-recipient customization.
        """
        try:
            # --- STEP 1: Fetch credentials from MongoDB ---
            mongo_client = MongoClient(os.getenv("MONGO_DB_URI"))
            db = mongo_client[os.getenv("DB_NAME")]
            collection = db["usercredentials"]

            user_doc = collection.find_one({"userEmail": self.user_email})
            if not user_doc:
                return {"status": "error", "summary": f"❌ No WhatsApp credentials found for {self.user_email}"}

            whatsapp_doc = user_doc.get("whatsapp", {})
            session_name = whatsapp_doc.get("sessionName")
            api_key = whatsapp_doc.get("apiKey")

            if not session_name or not api_key:
                return {"status": "error", "summary": f"❌ WhatsApp credentials missing for {self.user_email}"}

            # --- STEP 2: Initialize WhatsApp client ---
            async with WhatsAppClient(session_name=session_name, api_key=api_key) as client:
                print(f"[TOOL] Initialized WhatsApp session '{session_name}' for bulk sending")

                # Normalize messages: same for all or one per recipient
                if isinstance(message, str):
                    messages = [message] * len(recipients)
                elif isinstance(message, list) and len(message) == len(recipients):
                    messages = message
                else:
                    return {
                        "status": "error",
                        "summary": "❌ 'message' must be a string or a list matching the recipients length."
                    }

                # --- STEP 3: Send messages concurrently ---
                results = await asyncio.gather(
                    *[self._send_message(client, db, recipients[i], messages[i]) for i in range(len(recipients))],
                    return_exceptions=True
                )

                # --- STEP 4: Aggregate results ---
                successes = [r for r in results if isinstance(r, dict) and r.get("success")]
                failures = [r for r in results if not (isinstance(r, dict) and r.get("success"))]

                summary = (
                    f"✅ Sent {len(successes)} / {len(recipients)} messages successfully. "
                    f"❌ {len(failures)} failed."
                )

                return {
                    "status": "complete",
                    "summary": summary,
                    "successes": successes,
                    "failures": failures
                }

        except Exception as e:
            return {"status": "error", "summary": f"❌ WhatsApp bulk error: {e}"}

    # --- INTERNAL HELPER: Send one message and log it ---
    async def _send_message(self, client, db, to_number: str, message: str) -> Dict[str, Any]:
        """Send a single WhatsApp message and log it in MongoDB."""
        try:
            print(f"[TOOL] Sending WhatsApp message to {to_number}...")
            result = client.send_message(to_number, message)
            success = await result if inspect.isawaitable(result) else result

            clean_number = to_number.replace("@c.us", "")
            if not clean_number.startswith("+"):
                clean_number = "+" + clean_number

            if success:
                # Log message in database
                messages_col = db["whatsappmessages"]
                msg_entry = {"assistant": message, "time": datetime.utcnow()}

                existing = messages_col.find_one({
                    "user_email": self.user_email,
                    "to_number": clean_number
                })
                if existing:
                    messages_col.update_one(
                        {"_id": existing["_id"]},
                        {"$push": {"messages": msg_entry}, "$set": {"time": datetime.utcnow()}}
                    )
                else:
                    messages_col.insert_one({
                        "user_email": self.user_email,
                        "to_number": clean_number,
                        "time": datetime.utcnow(),
                        "messages": [msg_entry]
                    })

                print(f"[TOOL] ✅ Sent message to {clean_number}")
                return {"success": True, "to": clean_number, "message": message}

            else:
                print(f"[TOOL] ❌ Failed to send message to {clean_number}")
                return {"success": False, "to": clean_number, "error": "Send failed"}

        except Exception as e:
            print(f"[TOOL] ⚠️ Error sending to {to_number}: {e}")
            return {"success": False, "to": to_number, "error": str(e)}
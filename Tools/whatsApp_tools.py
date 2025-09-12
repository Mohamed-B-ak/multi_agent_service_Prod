# tools.py
import os
import requests
from typing import Optional
from crewai.tools import BaseTool

# -------- WhatsApp ----------
class WhatsAppTool(BaseTool):
    name: str = "WhatsApp Tool"
    description: str = (
        "Use for sending WhatsApp messages. Args: to_number(str), message(str). "
        "Sends messages via WhatsApp API."
    )

    async def _run(self, to_number: str, message: str) -> str:
        try:
            from whatsapp_client_python.whatsapp_client import WhatsAppClient
            
            # Initialize WhatsAppClient with session name and API key
            client = WhatsAppClient(
                session_name="8a41e673426e514ef82f705_tertertert",
                api_key="comp_mei6o0co_b5ebef99b36e2885b338a33ec3ba41f4"
            )

            # Use async context manager to handle the client session and send the message
            async with client as whatsapp_client:
                # Send the message to the given phone number
                success = await whatsapp_client.send_message(phone=to_number, message=message)

                # Log and return response
                if success:
                    return f"✅ WhatsApp message successfully sent to {to_number}: {message[:80]}"
                else:
                    return f"❌ Failed to send WhatsApp message to {to_number}: {message[:80]}"
        except Exception as e:
            return f"❌ WhatsApp error: {str(e)}"
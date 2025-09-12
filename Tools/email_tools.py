import os
import requests
from typing import Optional
from crewai.tools import BaseTool

# -------- Email (MailerSend) ----------
class MailerSendTool(BaseTool):
    name: str = "MailerSend Email Tool"
    description: str = "Sends an email using MailerSend API."

    def _run(self, to_email: str, subject: str, message: str) -> str:
        url = "https://api.mailersend.com/v1/email"
        headers = {
            "Authorization": f"Bearer mlsn.df1361445d5293256da9e99035266eb06e5d7524d118615be95401f0f2679b87",
            "Content-Type": "application/json"
        }
        data = {
            "from": {"email": "info@siyadah-ai.com", "name": "Siyadah"},
            "to": [{"email": to_email, "name": to_email.split('@')[0]}],
            "subject": subject,
            "text": message,
            "html": f"<p>{message}</p>"
        }
        print("ok")
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 202:
            return f"✅ Email accepted for delivery to {to_email}."
        else:
            return f"❌ Failed to send. Status: {response.status_code}, Error: {response.text}"
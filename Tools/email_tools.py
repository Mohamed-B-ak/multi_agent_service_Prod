import os
import requests
from crewai.tools import BaseTool
from pymongo import MongoClient

class MailerSendTool(BaseTool):
    name: str = "MailerSend Email Tool"
    description: str = "Sends an email using MailerSend API."

    # ✅ declare user_email as a Pydantic field
    user_email: str

    def _run(self, to_email: str, subject: str, message: str) -> str:
        print(self.user_email)
        try:
            client = MongoClient(os.getenv("MONGO_DB_URI"))
            db = client[os.getenv("DB_NAME")]
            collection = db["usercredentials"]

            # Find user document
            user_doc = collection.find_one({"userEmail": self.user_email})
            if not user_doc:
                return f"❌ No credentials found for {self.user_email}"

            mailer_doc = user_doc.get("mailerSend", {})
            sender = mailer_doc.get("sender")
            api_key = mailer_doc.get("apiKey")

            if not sender or not api_key:
                return "❌ MailerSend credentials are missing"

        except Exception as e:
            return f"❌ Error fetching credentials: {str(e)}"
        print(api_key)
        print(sender)
        # ✅ MailerSend API request
        url = "https://api.mailersend.com/v1/email"
        headers = {
            "Authorization": f"Bearer {api_key}",   # correct Bearer format
            "Content-Type": "application/json"
        }
        data = {
            "from": {"email": sender, "name": "Siyadah"},
            "to": [{"email": to_email, "name": to_email.split('@')[0]}],
            "subject": subject,
            "text": message,
            "html": f"<p>{message}</p>"
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            if response.status_code == 202:
                return f"✅ Email accepted for delivery to {to_email}."
            else:
                return f"❌ Failed to send. Status: {response.status_code}, Error: {response.text}"
        except Exception as e:
            return f"❌ Error sending email: {str(e)}"

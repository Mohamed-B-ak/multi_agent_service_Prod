import os
import requests
from datetime import datetime
from crewai.tools import BaseTool
from pymongo import MongoClient
from openai import OpenAI
class MailerSendTool(BaseTool):
    name: str = "MailerSend Email Tool"
    description: str = "Sends an email using MailerSend API."

    # ✅ declare user_email as a Pydantic field
    user_email: str

    def _run(self, to_email: str, subject: str, message: str) -> str:
        print(self.user_email)

        try: 
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

            prompt = f"""
            You are an assistant that formats emails professionally.
            Task:
            - Rewrite the subject line to be clear and professional.
            - Rewrite the message as a professional HTML email with paragraphs, optional bullet points, and links if needed.
            - Remove or replace any placeholders like {{name}} with neutral phrasing.

            Subject: {subject}
            Message: {message}
            """

            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )

            improved_text = response.choices[0].message.content

            # ✅ Split subject & HTML message
            if "Subject:" in improved_text and "HTML:" in improved_text:
                parts = improved_text.split("HTML:")
                new_subject = parts[0].replace("Subject:", "").strip()
                new_html = parts[1].strip()
            else:
                # fallback: keep subject same, just format body
                new_subject = subject
                new_html = f"<p>{improved_text}</p>"
        except: 
            print("error")
            new_subject = subject
            new_html = message

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
            "subject": new_subject,
            "text": message,   
            "html": new_html
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            if response.status_code == 202:
                # ✅ Save to DB after success
                try:
                    emails_collection = db["emailmessages"]  # will create if not exists
                    emails_collection.insert_one({
                        "user_email": self.user_email,
                        "to_email": to_email,
                        "time": datetime.utcnow(),
                        "email_subject": subject,
                        "email_content": message
                    })
                except Exception as e:
                    return f"✅ Email accepted for delivery to {to_email}, but failed to save: {e}"

                return f"✅ Email accepted for delivery to {to_email} and saved to DB."
            else:
                return f"❌ Failed to send. Status: {response.status_code}, Error: {response.text}"
        except Exception as e:
            return f"❌ Error sending email: {str(e)}"

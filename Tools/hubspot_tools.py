# tools/hubspot_tools.py

import os
from hubspot import HubSpot
from crewai.tools import BaseTool
from pymongo import MongoClient

class HubSpotContactsTool(BaseTool):
    name: str = "HubSpot Contacts Tool"
    description: str = "Fetches contacts from HubSpot including names, emails, and phone numbers."

    # ✅ user email injected per agent
    user_email: str

    def _run(self, limit: int = 10) -> str:
        """Fetch contacts from HubSpot CRM."""

        try:
            # Connect to MongoDB
            client = MongoClient(os.getenv("MONGO_DB_URI"))
            db = client[os.getenv("DB_NAME", "Call-Center")]
            collection = db["usercredentials"]

            # Get user credentials
            user_doc = collection.find_one({"userEmail": self.user_email})
            if not user_doc:
                return f"❌ No credentials found for {self.user_email}"

            hubspot_doc = user_doc.get("hubspot", {})
            api_key = hubspot_doc.get("apiKey", "")

            # Use fallback if not set in DB
            if not api_key:
                api_key = os.getenv("HUBSPOT_FALLBACK_KEY", "")
            api_key = os.getenv("HUBSPOT_API_KEY")
            #if not api_key:
                #return "❌ HubSpot API key is missing"

        except Exception as e:
            return f"❌ Error fetching credentials: {str(e)}"

        try:
            # Init HubSpot client
            hubspot_client = HubSpot(access_token=api_key)

            # Fetch contacts with phone
            response = hubspot_client.crm.contacts.basic_api.get_page(
                limit=limit,
                properties=["firstname", "lastname", "email", "phone", "mobilephone"]
            )

            # Build summaries
            results = []
            for contact in response.results:
                info = contact.properties
                summary = (
                    f"{info.get('firstname', '')} {info.get('lastname', '')} "
                    f"- {info.get('email', '')} "
                    f"- Phone: {info.get('phone', '') or info.get('mobilephone', '')}"
                )
                results.append(summary)

            if not results:
                return "⚠️ No contacts found."

            return "\n".join(results)

        except Exception as e:
            return f"❌ Error fetching contacts from HubSpot: {str(e)}"

# tools/hubspot_tools.py

""" import os
from hubspot import HubSpot
from crewai.tools import BaseTool
from pymongo import MongoClient

class HubSpotContactsTool(BaseTool):
    name: str = "HubSpot Contacts Tool"
    description: str = "Fetches contacts from HubSpot including names, emails, and phone numbers."

    # ✅ user email injected per agent
    user_email: str

    def _run(self, limit: int = 10) -> str:
        #Fetch contacts from HubSpot CRM.

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
            print("+++++++++++++++++++++++++++++++",api_key)
            # Use fallback if not set in DB
            if not api_key:
                return "❌ there is no HubSpot api key "
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
 """


# tools/crm_contacts_tool.py
from dotenv import load_dotenv
load_dotenv()
import os
import requests
from crewai.tools import BaseTool
from pymongo import MongoClient

class HubSpotContactsTool(BaseTool):
    name: str = "CRM Contacts Tool"
    description: str = (
        "Fetches contacts from any connected CRM (HubSpot, Microsoft Dynamics, Odoo, Google Contacts, etc.) "
        "using ApiDeck Unified API. Returns names, emails, and phone numbers."
    )

    # ✅ user email injected per agent
    user_email: str

    def _run(self, service_id: str = "hubspot", limit: int = 10) -> str:
        """Fetch contacts from the selected CRM via ApiDeck."""

        try:
            # Call ApiDeck Unified CRM API
            url = "https://unify.apideck.com/crm/contacts"
            headers = {
                "Authorization": f"Bearer {os.getenv('APIDECK_API_KEY')}",
                "x-apideck-app-id": os.getenv("APIDECK_APP_ID"),
                "x-apideck-consumer-id": self.user_email,
                "x-apideck-service-id": service_id,
            }

            response = requests.get(url, headers=headers, params={"limit": limit})

            if response.status_code != 200:
                return f"❌ Error from {service_id}: {response.status_code} {response.text}"

            data = response.json()
            contacts = data.get("data", [])

            if not contacts:
                return f"⚠️ No contacts found in {service_id}."

            # Build summaries
            results = []
            for c in contacts:
                name = c.get("name", "Unknown")
                email = c.get("emails", [{}])[0].get("email", "")
                phone = c.get("phone_numbers", [{}])[0].get("number", "")
                results.append(f"{name} - {email} - 📞 {phone}")

            return response.json()

        except Exception as e:
            return f"❌ Error fetching contacts from {service_id}: {str(e)}"

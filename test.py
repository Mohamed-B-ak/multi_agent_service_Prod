# tools/hubspot_tools.py

from hubspot import HubSpot
from crewai.tools import BaseTool
from typing import Optional
import os
from pymongo import MongoClient


# MongoDB connection
client = MongoClient("**********************************")
db = client["Call-Center"]
collection = db["usercredentials"]

user_email = "mohamed.ak@d10.sa"
# Find user document
user_doc = collection.find_one({"userEmail": user_email})
print(user_doc)

# Extract HubSpot API key from user document
hubspot_doc = user_doc.get("hubspot", {})
apiKey = hubspot_doc.get("apiKey")


if not apiKey:
    apiKey = "***********************************"

# Initialize HubSpot client
hubspot_client = HubSpot(access_token=apiKey)

# Fetch contacts
limit = 10  # set your desired limit
response = hubspot_client.crm.contacts.basic_api.get_page(
    limit=limit,
    properties=["firstname", "lastname", "email", "phone"]
)
print("----------------------------------------")
print(response)
print("----------------------------------------")
results = []
for contact in response.results:
    info = contact.properties
    summary = f"{info.get('firstname', '')} {info.get('lastname', '')} - {info.get('email', '') } - {info.get('phone', '') }"
    results.append(summary)

print("Contacts fetched:")
for r in results:
    print(r)

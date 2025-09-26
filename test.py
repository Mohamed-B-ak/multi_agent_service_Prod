from dotenv import load_dotenv
import os

load_dotenv()
import requests
import os
user_email = "mohamed.ak@d10.sa"
service_id = "hubspot"
limit = 10
print(os.getenv('APIDECK_API_KEY'))
print(os.getenv("APIDECK_APP_ID"))
# Call ApiDeck Unified CRM API
url = "https://unify.apideck.com/crm/contacts"
headers = {
    "Authorization": f"Bearer {os.getenv('APIDECK_API_KEY')}",
    "x-apideck-app-id": os.getenv("APIDECK_APP_ID"),
    "x-apideck-consumer-id": user_email,
    "x-apideck-service-id": service_id,
}

response = requests.get(url, headers=headers, params={"limit": limit})
print(response.json())
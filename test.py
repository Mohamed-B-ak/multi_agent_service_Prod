#!/usr/bin/env python3
"""
Simple script to connect to MongoDB Atlas and retrieve user credentials
for mohamed.ak@d10.sa from the UserCredentials collection
"""

from pymongo import MongoClient

# MongoDB Atlas connection string
# ⚠️ Replace <username>, <password>, <cluster-url>, and <db-name> with your actual values
MONGODB_URI = "*****************************************************"

# Database and collection
DATABASE_NAME = "Call-Center"
COLLECTION_NAME = "knowledgebases"

def get_user_credentials(user_email: str):
    """Fetch user credentials from MongoDB Atlas"""
    try:
        client = MongoClient(MONGODB_URI)
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]

        # Query for the user
        user_doc = collection.find_one({"createdByEmail": user_email})
        print(user_doc)
        print(type(user_doc))
        print(user_doc['mailerSend']['sender'])
        print(user_doc['mailerSend']['apiKey'])
        if user_doc:
            print("✅ User credentials found:")
            for key, value in user_doc.items():
                print(f"   {key}: {value}")
        else:
            print(f"❌ No credentials found for {user_email}")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    get_user_credentials("mohamed.ak@d10.sa")

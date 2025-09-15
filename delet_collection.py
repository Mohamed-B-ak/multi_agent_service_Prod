from pymongo import MongoClient
import os

# ⚠️ Replace with your actual connection string
MONGO_DB_URI="***************"
DB_NAME="********"

def delete_clients_collection():
    try:
        # Connect to MongoDB Atlas
        client = MongoClient(MONGO_DB_URI)
        db = client[DB_NAME]

        # Check if 'clients' collection exists
        if "clients" in db.list_collection_names():
            db.drop_collection("clients")
            print("✅ Collection 'clients' has been deleted.")
        else:
            print("⚠️ Collection 'clients' does not exist in this database.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    delete_clients_collection()

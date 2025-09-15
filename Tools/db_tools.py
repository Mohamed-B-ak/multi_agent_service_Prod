from pymongo import MongoClient
from crewai.tools import BaseTool
from crewai import Agent, LLM
from typing import Any, Optional
import os
import uuid
from datetime import datetime
# Base connection class (not inheriting from BaseTool)
class MongoDBConnection:
    def __init__(self, connection_string: str, db_name: str):
        self.client = MongoClient(os.getenv("MONGO_DB_URI"))
        self.db = self.client[os.getenv("DB_NAME")]

    def get_db(self):
        return self.db

class MongoDBListCollectionsTool(BaseTool):
    name: str = "MongoDB List Collections Tool"
    description: str = "Fetches a list of collections and their structure."
    db: Any = None  # Define as Pydantic field

    def __init__(self, connection: MongoDBConnection, **kwargs):
        super().__init__(**kwargs)
        self.db = connection.get_db()

    def _run(self) -> str:
        collections = self.db.list_collection_names()
        collection_info = {}
        for collection_name in collections:
            collection = self.db[collection_name]
            sample_document = collection.find_one()
            collection_info[collection_name] = list(sample_document.keys()) if sample_document else "No data"
        
        return str(collection_info)

    class Config:
        arbitrary_types_allowed = True

class MongoDBCreateDocumentTool(BaseTool):
    name: str = "MongoDB Create Document Tool"
    description: str = "Creates a new document in a specified collection. Automatically generates unique IDs and adds audit fields (createdBy, createdByEmail, userEmail, createdAt)."
    db: Any = None

    def __init__(self, connection: MongoDBConnection, **kwargs):
        super().__init__(**kwargs)
        self.db = connection.get_db()

    def _run(self, collection_name: str, document: dict) -> str:
        try:
            # Make a copy to avoid modifying the original document
            document_copy = document.copy()
            
            # Generate unique ID if not provided or if it's None/empty
            if 'id' not in document_copy or document_copy['id'] is None or document_copy['id'] == '':
                document_copy['id'] = str(uuid.uuid4())
            
            # Optional: Add creation timestamp
            if 'created_at' not in document_copy:
                document_copy['created_at'] = datetime.utcnow()
            
            collection = self.db[collection_name]
            result = collection.insert_one(document_copy)
            
            return f"Document created with MongoDB ID: {result.inserted_id}, Custom ID: {document_copy['id']}"
            
        except Exception as e:
            # Handle duplicate key errors specifically
            if "E11000" in str(e) and "duplicate key" in str(e):
                return f"Error: Duplicate ID detected. Please provide a unique ID value. Details: {str(e)}"
            return f"Error creating document: {str(e)}"

    class Config:
        arbitrary_types_allowed = True

class MongoDBUpdateDocumentTool(BaseTool):
    name: str = "MongoDB Update Document Tool"
    description: str = "Updates a document in a specified collection."
    db: Any = None

    def __init__(self, connection: MongoDBConnection, **kwargs):
        super().__init__(**kwargs)
        self.db = connection.get_db()

    def _run(self, collection_name: str, filter_query: dict, update_data: dict) -> str:
        collection = self.db[collection_name]
        result = collection.update_one(filter_query, {'$set': update_data})
        if result.matched_count > 0:
            return f"Document updated. Matched: {result.matched_count}, Modified: {result.modified_count}"
        else:
            return "No document found to update."

    class Config:
        arbitrary_types_allowed = True

class MongoDBDeleteDocumentTool(BaseTool):
    name: str = "MongoDB Delete Document Tool"
    description: str = "Deletes a document from a specified collection."
    db: Any = None

    def __init__(self, connection: MongoDBConnection, **kwargs):
        super().__init__(**kwargs)
        self.db = connection.get_db()

    def _run(self, collection_name: str, filter_query: dict) -> str:
        collection = self.db[collection_name]
        result = collection.delete_one(filter_query)
        if result.deleted_count > 0:
            return f"Document deleted. Deleted count: {result.deleted_count}"
        else:
            return "No document found to delete."

    class Config:
        arbitrary_types_allowed = True

class MongoDBReadDataTool(BaseTool):
    name: str = "MongoDB Read Data Tool"
    description: str = "Reads data from a specified collection."
    db: Any = None

    def __init__(self, connection: MongoDBConnection, **kwargs):
        super().__init__(**kwargs)
        self.db = connection.get_db()

    def _run(self, collection_name: str, filter_query: Optional[dict] = None, limit: int = 10) -> str:
        collection = self.db[collection_name]
        cursor = collection.find(filter_query or {}).limit(limit)
        data = list(cursor)
        if data:
            return str(data)
        else:
            return "No data found."

    class Config:
        arbitrary_types_allowed = True

class MongoDBCountDocumentsTool(BaseTool):
    name: str = "MongoDB Count Documents Tool"
    description: str = "Counts the number of documents in a specified collection, always scoped by user email."
    db: Any = None
    user_email: str = None  # <-- add user email to the tool

    def __init__(self, connection: MongoDBConnection, user_email: str, **kwargs):
        super().__init__(**kwargs)
        self.db = connection.get_db()
        self.user_email = user_email

    def _apply_user_scope(self, query: Optional[dict]) -> dict:
        """Ensure all queries are scoped to the current user email."""
        user_filter = {
            "$or": [
                {"createdBy": self.user_email},
                {"createdByEmail": self.user_email},
                {"userEmail": self.user_email}
            ]
        }

        # No query provided → just return user scope
        if not query:
            return user_filter

        # If query already contains a user email condition → ignore it, use $or instead
        if any(k in query for k in ["createdBy", "createdByEmail", "userEmail"]):
            return user_filter

        # Otherwise, combine user filter with the provided query
        return {"$and": [query, user_filter]}
    
    def _run(self, collection_name: str, filter_query: Optional[dict] = None) -> str:
        collection = self.db[collection_name]
        scoped_query = self._apply_user_scope(filter_query)
        count = collection.count_documents(scoped_query)
        return f"Number of documents in '{collection_name}' for {self.user_email}: {count}"

    class Config:
        arbitrary_types_allowed = True
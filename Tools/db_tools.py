from pymongo import MongoClient
from crewai.tools import BaseTool
from crewai import Agent, LLM
from typing import Any, Optional
import os
import uuid
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, Dict, List
from bson import ObjectId
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

    def _run(self):
        """
        Lists all collections and their sample fields in the connected MongoDB database.
        Returns structured output for CrewAI compatibility.
        """
        try:
            collections = self.db.list_collection_names()
            collection_info = {}

            for collection_name in collections:
                collection = self.db[collection_name]
                sample_document = collection.find_one()
                collection_info[collection_name] = (
                    list(sample_document.keys()) if sample_document else []
                )

            return {
                "status": "success",
                "message": f"✅ Found {len(collections)} collections in the database.",
                "count": len(collections),
                "collections": collection_info
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"❌ Error listing collections: {e}",
                "count": 0,
                "collections": {}
            }


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

    def _run(self, collection_name: str, filter_query: dict, update_data: dict):
        """
        Updates one document in a MongoDB collection and returns structured output.
        """
        try:
            collection = self.db[collection_name]
            result = collection.update_one(filter_query, {"$set": update_data})

            if result.matched_count > 0:
                return {
                    "status": "success",
                    "message": (
                        f"✅ Document updated in '{collection_name}'. "
                        f"Matched: {result.matched_count}, Modified: {result.modified_count}"
                    ),
                    "collection": collection_name,
                    "matched_count": result.matched_count,
                    "modified_count": result.modified_count,
                    "filter": filter_query,
                    "update_data": update_data
                }
            else:
                return {
                    "status": "empty",
                    "message": f"ℹ️ No document found in '{collection_name}' matching filter {filter_query}.",
                    "collection": collection_name,
                    "matched_count": 0,
                    "modified_count": 0,
                    "filter": filter_query,
                    "update_data": update_data
                }

        except Exception as e:
            return {
                "status": "error",
                "message": f"❌ Error updating document in '{collection_name}': {e}",
                "collection": collection_name
            }


    class Config:
        arbitrary_types_allowed = True

class MongoDBDeleteDocumentTool(BaseTool):
    name: str = "MongoDB Delete Document Tool"
    description: str = "Deletes a document from a specified collection."
    db: Any = None

    def __init__(self, connection: MongoDBConnection, **kwargs):
        super().__init__(**kwargs)
        self.db = connection.get_db()

    def _run(self, collection_name: str, filter_query: dict):
        """
        Deletes one document from a MongoDB collection and returns structured output.
        """
        try:
            collection = self.db[collection_name]
            result = collection.delete_one(filter_query)

            if result.deleted_count > 0:
                # ✅ Structured success response
                return {
                    "status": "success",
                    "message": f"✅ Document deleted successfully from '{collection_name}'.",
                    "collection": collection_name,
                    "deleted_count": result.deleted_count,
                    "filter": filter_query
                }
            else:
                # ✅ Structured empty response (no match found)
                return {
                    "status": "empty",
                    "message": f"ℹ️ No document found in '{collection_name}' matching filter {filter_query}.",
                    "collection": collection_name,
                    "deleted_count": 0,
                    "filter": filter_query
                }

        except Exception as e:
            # ✅ Structured error response
            return {
                "status": "error",
                "message": f"❌ Error deleting document from '{collection_name}': {e}",
                "collection": collection_name
            }


    class Config:
        arbitrary_types_allowed = True

class MongoDBReadDataToolSchema(BaseModel):
    collection_name: str
    filter_query: Optional[Dict] = None
    limit: Optional[int] = 100

class MongoDBReadDataTool(BaseTool):
    name: str = "MongoDB Read Data Tool"
    description: str = "Reads data from a specified MongoDB collection."
    args_schema: type[BaseModel] = MongoDBReadDataToolSchema
    db: Any = None

    def __init__(self, connection: MongoDBConnection, **kwargs):
        super().__init__(**kwargs)
        self.db = connection.get_db()

    def _run(
        self,
        collection_name: str,
        filter_query: Optional[dict] = None,
        limit: int = 100,
        skip: int = 0
    ) -> dict:
        """Read documents from a MongoDB collection with optional filters and pagination."""
        try:
            collection = self.db[collection_name]
            cursor = collection.find(filter_query or {}).skip(skip).limit(limit)
            data = list(cursor)

            # Convert ObjectIds to strings for safe serialization
            for doc in data:
                if "_id" in doc and isinstance(doc["_id"], ObjectId):
                    doc["_id"] = str(doc["_id"])

            if data:
                return {
                    "success": True,
                    "status": "success",
                    "message": f"✅ Retrieved {len(data)} records from '{collection_name}'.",
                    "collection": collection_name,
                    "count": len(data),
                    "data": data
                }
            else:
                return {
                    "success": True,
                    "status": "empty",
                    "message": f"ℹ️ No documents found in '{collection_name}' for filter {filter_query or {}}.",
                    "collection": collection_name,
                    "count": 0,
                    "data": []
                }

        except Exception as e:
            return {
                "success": False,
                "status": "error",
                "message": f"❌ Error reading data from '{collection_name}': {e}"
            }

    class Config:
        arbitrary_types_allowed = True

class MongoDBBulkDeleteTool(BaseTool):
    name: str = "MongoDB Bulk Delete Tool"
    description: str = "Deletes multiple documents from a specified MongoDB collection based on a filter query."
    db: Any = None

    def __init__(self, connection: MongoDBConnection, **kwargs):
        super().__init__(**kwargs)
        self.db = connection.get_db()

    def _run(self, collection_name: str, filter_query: Optional[dict] = None, confirm: bool = False) -> dict:
        """
        Deletes multiple documents from a MongoDB collection.
        If `filter_query` is empty, requires `confirm=True` to avoid deleting the entire collection.
        """
        try:
            collection = self.db[collection_name]
            filter_query = filter_query or {}

            # Safety check to prevent accidental full collection wipe
            if not filter_query and not confirm:
                return {
                    "status": "blocked",
                    "message": (
                        "⚠️ No filter provided. Use 'confirm=True' if you really want to delete ALL documents."
                    ),
                    "collection": collection_name,
                    "deleted_count": 0,
                    "filter": {}
                }

            # Perform bulk deletion
            result = collection.delete_many(filter_query)

            if result.deleted_count > 0:
                return {
                    "status": "success",
                    "message": f"✅ Deleted {result.deleted_count} documents from '{collection_name}'.",
                    "collection": collection_name,
                    "deleted_count": result.deleted_count,
                    "filter": filter_query
                }
            else:
                return {
                    "status": "empty",
                    "message": f"ℹ️ No documents matched the filter {filter_query} in '{collection_name}'.",
                    "collection": collection_name,
                    "deleted_count": 0,
                    "filter": filter_query
                }

        except Exception as e:
            return {
                "status": "error",
                "message": f"❌ Error deleting documents from '{collection_name}': {e}",
                "collection": collection_name,
                "deleted_count": 0,
                "filter": filter_query or {}
            }

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
        if any(k in query for k in ["userEmail"]):
            return user_filter

        # Otherwise, combine user filter with the provided query
        return {"$and": [query, user_filter]}
    
    def _run(self, collection_name: str, filter_query: Optional[dict] = None) -> str:
        collection = self.db[collection_name]
        scoped_query = self._apply_user_scope(filter_query)
        count = collection.count_documents(scoped_query)
        return {
        "status": "success",
        "count": count,
        "message": f"✅ Current number of clients: {count}"
    }

    class Config:
        arbitrary_types_allowed = True

class MongoDBBulkCreateTool(BaseTool):
    name: str = "MongoDB Bulk Create Tool"
    description: str = (
        "Inserts multiple documents into a specified MongoDB collection. "
        "Automatically assigns unique IDs (`id`) and adds audit fields "
        "(`created_at`, `createdBy`, `createdByEmail`, `userEmail`)."
    )
    db: Any = None

    def __init__(self, connection: MongoDBConnection, **kwargs):
        super().__init__(**kwargs)
        self.db = connection.get_db()

    def _run(self, collection_name: str, documents: List[dict]) -> dict:
        """
        Creates multiple documents in a MongoDB collection.
        Adds default audit fields and generates unique IDs where missing.
        """
        try:
            if not documents or not isinstance(documents, list):
                return {
                    "status": "error",
                    "message": "❌ Input must be a non-empty list of documents.",
                    "collection": collection_name,
                    "inserted_count": 0,
                    "inserted_ids": []
                }

            prepared_docs = []
            for doc in documents:
                doc_copy = doc.copy()

                # Auto-generate custom UUID if missing
                if not doc_copy.get("id"):
                    doc_copy["id"] = str(uuid.uuid4())

                # Add creation timestamp
                doc_copy.setdefault("created_at", datetime.utcnow())

                # Optional audit fields (kept flexible)
                doc_copy.setdefault("createdBy", "system")
                doc_copy.setdefault("createdByEmail", "system@auto")
                doc_copy.setdefault("userEmail", "system@auto")

                prepared_docs.append(doc_copy)

            collection = self.db[collection_name]
            result = collection.insert_many(prepared_docs)

            return {
                "status": "success",
                "message": f"✅ Successfully inserted {len(result.inserted_ids)} documents into '{collection_name}'.",
                "collection": collection_name,
                "inserted_count": len(result.inserted_ids),
                "inserted_ids": [str(_id) for _id in result.inserted_ids],
                "custom_ids": [doc["id"] for doc in prepared_docs]
            }

        except Exception as e:
            if "E11000" in str(e) and "duplicate key" in str(e):
                return {
                    "status": "error",
                    "message": f"❌ Duplicate key error while inserting documents: {e}",
                    "collection": collection_name,
                    "inserted_count": 0
                }
            return {
                "status": "error",
                "message": f"❌ Error creating documents in '{collection_name}': {e}",
                "collection": collection_name,
                "inserted_count": 0
            }

    class Config:
        arbitrary_types_allowed = True

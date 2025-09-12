from pymongo import MongoClient
from crewai.tools import BaseTool
from crewai import Agent, LLM
from typing import Any, Optional

# Base connection class (not inheriting from BaseTool)
class MongoDBConnection:
    def __init__(self, connection_string: str, db_name: str):
        self.client = MongoClient(connection_string)
        self.db = self.client[db_name]

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
    description: str = "Creates a new document in a specified collection."
    db: Any = None

    def __init__(self, connection: MongoDBConnection, **kwargs):
        super().__init__(**kwargs)
        self.db = connection.get_db()

    def _run(self, collection_name: str, document: dict) -> str:
        collection = self.db[collection_name]
        result = collection.insert_one(document)
        return f"Document created with ID: {result.inserted_id}"

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
    description: str = "Counts the number of documents in a specified collection."
    db: Any = None

    def __init__(self, connection: MongoDBConnection, **kwargs):
        super().__init__(**kwargs)
        self.db = connection.get_db()

    def _run(self, collection_name: str, filter_query: Optional[dict] = None) -> str:
        collection = self.db[collection_name]
        count = collection.count_documents(filter_query or {})
        return f"Number of documents in '{collection_name}': {count}"

    class Config:
        arbitrary_types_allowed = True
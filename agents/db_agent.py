from crewai import Agent
import os
from Tools.db_tools import (
    MongoDBConnection,
    MongoDBListCollectionsTool,
    MongoDBCreateDocumentTool,
    MongoDBUpdateDocumentTool,
    MongoDBDeleteDocumentTool,
    MongoDBReadDataTool,
    MongoDBCountDocumentsTool
)

def db_agent(llm_obj, user_language="en") -> Agent:
    """
    MongoDB agent that performs CRUD and aggregation operations,
    ensuring all outputs and queries are in the user's language and
    restricted to the user's email context.

    Args:
        llm_obj: LLM instance to use for generation.
        user_language: Language code of the user's input ('en', 'ar', etc.)

    Returns:
        Agent instance
    """

    # Create connection object (not a tool)
    connection = MongoDBConnection(
        connection_string=os.getenv("MONGO_DB_URI"), 
        db_name=os.getenv("DB_NAME")
    )
    
    # Create tools with the connection
    list_collections_tool = MongoDBListCollectionsTool(connection)
    create_document_tool = MongoDBCreateDocumentTool(connection)
    update_document_tool = MongoDBUpdateDocumentTool(connection)
    delete_document_tool = MongoDBDeleteDocumentTool(connection)
    read_data_tool = MongoDBReadDataTool(connection)
    count_documents_tool = MongoDBCountDocumentsTool(connection)

    goal_text = (
        "Perform operations on MongoDB Atlas, such as listing collections, describing their structure, "
        "counting documents, and executing CRUD or aggregation queries. "
        f"⚠️ Respond ONLY in the user's language: {user_language}, "
        "and ensure all operations are restricted to the user's email context."
    )

    backstory_text = (
        "You are an expert in MongoDB Atlas operations. "
        f"You can list collections, describe collection structures, count documents, "
        f"perform CRUD operations (Create, Read, Update, Delete), and aggregation queries. "
        f"All outputs and explanations must strictly be in {user_language} "
        "and linked to the user's email context."
    )

    return Agent(
        name="MongoDBAgent",
        role="MongoDB Database Specialist",
        goal=goal_text,
        backstory=backstory_text,
        tools=[
            list_collections_tool,
            create_document_tool,
            update_document_tool,
            delete_document_tool,
            read_data_tool,
            count_documents_tool,
        ],
        allow_delegation=False,
        llm=llm_obj,
        verbose=True,
        max_retry_limit=1,
    )

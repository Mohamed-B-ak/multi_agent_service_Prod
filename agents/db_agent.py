from crewai import Agent
import os
from Tools.db_tools import (
    MongoDBConnection,
    MongoDBListCollectionsTool,
    MongoDBCreateDocumentTool,
    MongoDBUpdateDocumentTool,
    MongoDBDeleteDocumentTool,
    MongoDBReadDataTool,
    MongoDBCountDocumentsTool,
    MongoDBBulkDeleteTool,
    MongoDBBulkCreateTool,
)

def db_agent(llm_obj, user_email, user_language="en") -> Agent:
    """
    MongoDB agent that performs CRUD and aggregation operations,
    ensuring all outputs and queries are in the user's language and
    restricted to the user's email context.

    Args:
        llm_obj: LLM instance to use for generation.
        user_email: Email of the current user to scope queries.
        user_language: Language code of the user's input ('en', 'ar', etc.)

    Returns:
        Agent instance
    """

    # Create connection object (not a tool)
    connection = MongoDBConnection(
        connection_string=os.getenv("MONGO_DB_URI"), 
        db_name=os.getenv("DB_NAME")
    )
    
    # Tools
    list_collections_tool = MongoDBListCollectionsTool(connection)
    create_document_tool = MongoDBCreateDocumentTool(connection)
    create_bulk_document_tool = MongoDBBulkCreateTool(connection)
    update_document_tool = MongoDBUpdateDocumentTool(connection)
    delete_document_tool = MongoDBDeleteDocumentTool(connection)
    delete_bulk_document_tool = MongoDBBulkDeleteTool(connection)
    read_data_tool = MongoDBReadDataTool(connection)
    count_documents_tool = MongoDBCountDocumentsTool(connection, user_email)


    # 🔹 Get available collections and fields
    collections_info = list_collections_tool._run()

    goal_text = (
        "Perform operations on MongoDB Atlas, such as listing collections, describing their structure, "
        "counting documents, and executing CRUD or aggregation queries. "
        f"⚠️ Respond ONLY in the user's language: {user_language}. "
        f"Always restrict queries to the user's email: {user_email}, by filtering against  of the field: "
        "`userEmail`. "
        f"\n\nAvailable collections and fields: {collections_info}."
        "\nPick the most relevant collection for the user’s request. "
        "Do NOT invent collection names — always choose from the above."
        f"All answers must be strictly in {user_language}, concise, accurate, "
        "the key source should be internal "
    )

    backstory_text = (
        "You are an expert in MongoDB Atlas operations. "
        f"You can list collections, describe collection structures, count documents, "
        f"perform CRUD operations (Create, Read, Update, Delete), and aggregation queries. "
        f"All outputs and explanations must strictly be in {user_language}. "
        "All queries must be scoped by the user's email. "
        f"\n\nYou have access to these collections: {collections_info}. "
        "Always pick the best match for the request (e.g., if the user asks about 'clients' "
        "but only 'customers' exists, use 'customers')."
        f"All answers must be strictly in {user_language}, concise, accurate, "
        "the key source should be internal "
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
            delete_bulk_document_tool,
            create_bulk_document_tool,
        ],
        allow_delegation=False,
        llm=llm_obj,
        verbose=True,
        result_parser=handle_output,
    )

def handle_output(result):
    # Stop re-calling tools once a valid result is found
    if isinstance(result, dict) and result.get("status") == "success":
        print("✅ Task completed successfully, stopping agent loop.")
        return result["message"]
    return result
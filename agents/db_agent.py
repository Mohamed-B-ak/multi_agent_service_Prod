from crewai import Agent
from crewai import Agent
import os
from Tools.db_tools import MongoDBConnection, MongoDBListCollectionsTool, MongoDBCreateDocumentTool, MongoDBUpdateDocumentTool, MongoDBDeleteDocumentTool, MongoDBReadDataTool, MongoDBCountDocumentsTool

def db_agent(llm_obj) -> Agent:
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

    return Agent(
        name="MongoDBAgent",
        role="MongoDB Database Specialist",
        goal=(
            "Perform operations on MongoDB Atlas, such as listing collections, describing their structure, "
            "counting documents, and executing CRUD or aggregation queries."
        ),
        backstory=(
            "You are an expert in MongoDB Atlas operations. You can list collections, describe the "
            "structure of collections, count documents, and perform CRUD operations (Create, Read, Update, Delete), "
            "as well as aggregation queries."
        ),
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

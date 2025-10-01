import os
from crewai import Agent, LLM

# 🔹 Database tools
from Tools.db_tools import (
    MongoDBConnection,
    MongoDBListCollectionsTool,
    MongoDBCreateDocumentTool,
    MongoDBUpdateDocumentTool,
    MongoDBDeleteDocumentTool,
    MongoDBReadDataTool,
    MongoDBCountDocumentsTool
)
from Tools.whatsApp_tools import WhatsAppTool
from Tools.email_tools import MailerSendTool


from dotenv import load_dotenv
import os

load_dotenv()

def sales_agent(llm_obj, user_email, user_language="en") -> Agent:
    """
    Sales agent that performs MongoDB CRUD/aggregation operations,
    prepares sales campaign content, and sends it via WhatsApp or Email.
    Ensures all outputs and queries are in the user's language and 
    restricted to the user's email context.
    """

    # Database connection
    connection = MongoDBConnection(
        connection_string=os.getenv("MONGO_DB_URI"),
        db_name=os.getenv("DB_NAME")
    )

    # Database Tools
    list_collections_tool = MongoDBListCollectionsTool(connection)
    create_document_tool = MongoDBCreateDocumentTool(connection)
    update_document_tool = MongoDBUpdateDocumentTool(connection)
    delete_document_tool = MongoDBDeleteDocumentTool(connection)
    read_data_tool = MongoDBReadDataTool(connection)
    count_documents_tool = MongoDBCountDocumentsTool(connection, user_email)

    # Sales Tools
    # Sales Tools
    whatsapp_tool = WhatsAppTool(user_email=user_email)
    email_tool = MailerSendTool(user_email=user_email)

   

    # Collections info
    collections_info = list_collections_tool._run()

    # Goal
    goal_text = (
        "As a Sales Agent, perform MongoDB Atlas operations (list collections, "
        "CRUD, aggregations) AND prepare personalized sales campaign content. "
        "You can send campaign content via WhatsApp or Email. "
        f"⚠️ Respond ONLY in the user's language: {user_language}. "
        f"Always restrict database queries to the user's email: {user_email}, "
        "by filtering against fields like `createdBy`, `createdByEmail`, `userEmail`. "
        f"\n\nAvailable collections and fields: {collections_info}. "
        "Always choose the most relevant collection. Do NOT invent names."
        f"\n\nSales duties: generate persuasive messages, email campaigns, "
        "WhatsApp outreach, and ensure professional tone."
    )

    # Backstory
    backstory_text = (
        "You are a Sales Agent who specializes in CRM and outreach automation. "
        "You understand MongoDB Atlas and can perform CRUD and aggregation queries, "
        "but you are also an expert in creating and sending marketing campaigns. "
        "You craft high-conversion content, then deliver it to prospects through "
        "WhatsApp or Email using prepared tools. "
        f"All outputs must strictly be in {user_language}, concise and accurate. "
        "Database operations must always be scoped to the user’s email context."
    )

    return Agent(
        name="SalesAgent",
        role="Sales & CRM Automation Specialist",
        goal=goal_text,
        backstory=backstory_text,
        tools=[
            list_collections_tool,
            create_document_tool,
            update_document_tool,
            delete_document_tool,
            read_data_tool,
            count_documents_tool,
            whatsapp_tool,
            email_tool
        ],
        allow_delegation=False,
        llm=llm_obj,
        verbose=True,
    )


if __name__ == "__main__":
    # 🔹 Setup your LLM
    llm = LLM(
        model="gpt-3.5-turbo",
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.1,
        max_tokens=500,
    )
    # 🔹 Create the agent
    agent = sales_agent(llm, user_email="mohamed.ak@d10.sa", user_language="en")

    # 🔹 Run the agent with a request
    result = agent.kickoff("Create a WhatsApp campaign for new leads in Dubai about our new product launch, and give me the phone numbers of the client who has thi email mohamed.ak@d10.sa and finally send a whatsApp message to mohamed .")

    print("\n--- Agent Output ---")
    print(result.raw)

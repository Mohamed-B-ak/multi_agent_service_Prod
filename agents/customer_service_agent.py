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

# 🔹 Communication tools
from Tools.whatsApp_tools import WhatsAppTool
from Tools.email_tools import MailerSendTool

from dotenv import load_dotenv
load_dotenv()

def customer_service_agent(llm_obj, user_email, user_language) -> Agent:
    """
    Customer Service agent that receives customer messages,
    understands intent, generates contextual replies,
    and sends them via WhatsApp or Email.
    Ensures outputs and queries are in the customer's language
    and restricted to the user's email context.
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

    # Communication Tools
    whatsapp_tool = WhatsAppTool(user_email=user_email)
    email_tool = MailerSendTool(user_email=user_email)

    # Collections info
    try:
        collections_info = list_collections_tool._run()
    except Exception as e:
        collections_info = f"⚠️ Could not fetch collections: {e}"

    # Goal
    goal_text = (
        "As a Customer Service Agent, you receive, analyze, and respond to customer messages "
        "via WhatsApp or Email. Core responsibilities:\n"
        "1) Detect customer intent (greetings, questions, complaints, requests).\n"
        "2) Generate professional, helpful replies in the customer’s language.\n"
        "3) Format channel-appropriate replies (WhatsApp = short & friendly, Email = formal).\n"
        "4) Send the reply immediately using WhatsAppTool or MailerSendTool.\n"
        "5) Handle greetings warmly in any language.\n"
        "6) Never use placeholders – always reply contextually.\n\n"
        f"⚠️ Respond ONLY in the user’s language: {user_language}. "
        f"Always restrict database queries to the user’s email: {user_email}, "
        "by filtering against fields like `userEmail`. "
        f"\n\nAvailable collections and fields: {collections_info}. "
        "Always choose the most relevant collection. Do NOT invent names."
    )

    # Backstory
    backstory_text = (
        "You are a Customer Service Specialist with expertise in multi-channel support. "
        "You’ve successfully handled over 100,000 interactions with high satisfaction rates. "
        "Your superpower is detecting intent, emotions, and urgency from minimal input, "
        "and replying instantly with empathy and professionalism.\n\n"
        f"All outputs must strictly be in {user_language}, concise and accurate. "
        "Database operations must always be scoped to the user’s email context. "
        "You maintain conversation continuity, handle complaints with care, "
        "and always provide clear solutions or clarifying questions."
    )

    return Agent(
        name="CustomerServiceAgent",
        role="Unified Customer Service Specialist",
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

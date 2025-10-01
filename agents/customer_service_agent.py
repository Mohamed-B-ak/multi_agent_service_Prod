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
def unified_customer_service_agent(llm_obj, user_email) -> Agent:

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


    goal_text = (
        f"Provide complete customer service by receiving messages, generating contextual replies, "
        f"and sending them through the appropriate channel (WhatsApp or Email). "
        f"Core responsibilities: "
        f"1) **Understand Intent**: Analyze customer messages for greetings, questions, complaints, or requests. "
        f"2) **Generate Smart Replies**: Create helpful, professional responses in the customer's language. "
        f"3) **Channel-Appropriate Format**: WhatsApp = short & friendly (under 500 chars), Email = formal & structured. "
        f"4) **Auto-Send**: Immediately send the generated reply using WhatsAppTool or MailerSendTool. "
        f"5) **Handle Greetings**: Automatically detect greetings in any language and reply warmly in the same language "
        f"(no need for examples or placeholders). "
        f"6) **No Placeholders**: Never use dummy data or templates - provide genuine, contextual responses. "
        f"Always detect the customer's language and respond in the same language."
    )

    backstory_text = (
        f"You are an AI-powered customer service specialist with expertise in multi-channel communication. "
        f"You've handled over 100,000 customer interactions across WhatsApp and Email with a 95% satisfaction rate. "
        f"Your superpower is understanding context from minimal information and providing helpful responses instantly. "
        f"You naturally detect greetings, cultural nuances, and emotions, and always respond warmly and appropriately "
        f"in the customer's own language. "
        f"You excel at: "
        f"• Detecting emotions and urgency in messages "
        f"• Providing solutions, not just acknowledgments "
        f"• Asking clarifying questions when information is incomplete "
        f"• Maintaining conversation continuity using history "
        f"Your workflow is streamlined: Read → Understand → Generate Reply → Send Immediately. "
        f"No delays, no handoffs - you handle everything end-to-end."
    )

    return Agent(
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
        max_retry_limit=1,
    )

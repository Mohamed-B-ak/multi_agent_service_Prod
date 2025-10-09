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
    MongoDBCountDocumentsTool,
    MongoDBBulkDeleteTool,
    MongoDBBulkCreateTool
)

# 🔹 Communication tools
from Tools.whatsApp_tools import WhatsAppTool, WhatsAppBulkSenderTool
from Tools.email_tools import MailerSendTool
from Tools.MessageContentTool import MessageContentTool

from utils import standard_result_parser
from dotenv import load_dotenv
load_dotenv()


def marketing_agent(llm_obj, user_email, user_language) -> Agent:
    """
    Marketing agent that performs MongoDB CRUD/aggregation operations,
    prepares marketing campaign content, segments customers,
    and sends content via WhatsApp or Email.
    Ensures all outputs and queries are in the user's language
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
    delete_bulk_document_tool = MongoDBBulkDeleteTool(connection)
    create_bulk_document_tool = MongoDBBulkCreateTool(connection)
    read_data_tool = MongoDBReadDataTool(connection)
    count_documents_tool = MongoDBCountDocumentsTool(connection, user_email)

    # Marketing Tools
    whatsapp_tool = WhatsAppTool(user_email=user_email)
    whatsapp_bulk_tool = WhatsAppBulkSenderTool(user_email=user_email)
    email_tool = MailerSendTool(user_email=user_email)
    content_tool = MessageContentTool(user_email=user_email)

    # Collections info
    collections_info = list_collections_tool._run()

    # ✅ Updated Goal Text — now explicitly allows tool execution
    goal_text = (
        f"🎯 **PRIMARY RULE**: You are a Marketing Agent who EXECUTES actions, not describes them.\n\n"
        
        f"📨 **Message Sending Rules**:\n"
        f"1. **Single Message**: User says 'send to Mohamed' → Use WhatsAppTool(to_number, message)\n"
        f"2. **Bulk Messages**: User says 'send to all customers' → Use WhatsAppBulkSenderTool(recipients, message)\n"
        f"   - recipients must be a LIST of phone numbers from database\n"
        f"   - message can be string (same for all) or list (personalized)\n\n"
        
        f"⚠️ **CRITICAL VERIFICATION STEPS**:\n"
        f"Step 1: Get phone numbers from MongoDB using MongoDBReadDataTool\n"
        f"Step 2: Extract phone numbers into a Python list\n"
        f"Step 3: Call WhatsAppBulkSenderTool with the list\n"
        f"Step 4: VERIFY tool returned {{\"status\": \"complete\", \"successes\": [...]}}\n"
        f"Step 5: ONLY THEN say 'تم الإرسال'\n\n"
        
        f"❌ **FORBIDDEN**:\n"
        f"- Saying 'تم الإرسال' without calling WhatsAppTool/WhatsAppBulkSenderTool\n"
        f"- Using MongoDB read results as proof of sending\n"
        f"- Assuming success without tool confirmation\n\n"
        
        f"📊 **Success Criteria for Bulk Sending**:\n"
        f"✅ Tool call logged in execution trace\n"
        f"✅ Tool returned status='complete'\n"
        f"✅ successes count > 0\n"
        f"✅ Each success has {{\"to\": phone, \"success\": true}}\n\n"
        
        f"Always respond in {user_language}. Database: {collections_info}. User: {user_email}"
    )


    # ✅ Updated Backstory Text — supports automatic sending
    backstory_text = (
        f"You are a precise Marketing Agent who executes instructions exactly as requested. "
        f"When the user explicitly asks to send a message, "
        f"you MUST actually send it using the right tool, not just describe the action. "
        f"For example, when the user says 'send a WhatsApp message', "
        f"use the WhatsAppTool to send it to the provided number.\n\n"
        f"You can also prepare and analyze campaigns when the user says 'prepare' or 'draft'. "
        f"Always respond in {user_language} and restrict all database operations "
        f"to the user’s email: {user_email}."
    )

    return Agent(
        name="MarketingAgent",
        role="Marketing & Campaign Specialist",
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
            whatsapp_bulk_tool,
            email_tool,
            content_tool,
            delete_bulk_document_tool,
            create_bulk_document_tool
        ],
        allow_delegation=False,
        llm=llm_obj,
        verbose=True,
        result_parser=standard_result_parser,
    )


def handle_output(result):
    # ✅ Enforce real tool execution check
    if isinstance(result, dict):
        if result.get("status") == "success":
            print("✅ WhatsAppTool executed successfully.")
            return result.get("message", "")
        elif "تم إرسال" in str(result).lower() and "status" not in result:
            print("⚠️ Fake send detected — WhatsAppTool was not used.")
            return "⚠️ The message was described as sent, but the WhatsApp tool did not actually execute."


if __name__ == "__main__":
    # 🔹 Setup your LLM
    llm = LLM(
        model="gpt-3.5-turbo",
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.2,
        max_tokens=700,
    )

    # 🔹 Create the agent
    agent = marketing_agent(llm, user_email="mohamed.ak@d10.sa", user_language="en")

    # 🔹 Example: Run the agent with a marketing task
    result = agent.kickoff("send a WhatsApp welcome message to Akacha Mohamed at +21653844063 content : Salam Mohamed! أهلا وسهلا بيك في فريقنا الجديد. نورتنا وإن شاء الله تكون فترة ممتعة ومفيدة معانا. تواصل معنا إذا احتجت أي مساعدة. 😊🎉 ")

    print("\n--- Agent Output ---")
    print(result.raw)

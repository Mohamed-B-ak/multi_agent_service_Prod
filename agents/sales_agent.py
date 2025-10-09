"""
Flexible Sales Agent - Smart and Adaptive
يتعامل بذكاء مع الطلبات ويأخذ المبادرة عند الحاجة
"""

import os
from crewai import Agent
from datetime import datetime

# Database tools
from Tools.db_tools import (
    MongoDBConnection,
    MongoDBListCollectionsTool,
    MongoDBCreateDocumentTool,
    MongoDBUpdateDocumentTool,
    MongoDBDeleteDocumentTool,
    MongoDBReadDataTool,
    MongoDBCountDocumentsTool, MongoDBBulkDeleteTool, MongoDBBulkCreateTool
)

# Communication tools
from Tools.whatsApp_tools import WhatsAppTool, WhatsAppBulkSenderTool
from Tools.email_tools import MailerSendTool
from Tools.MessageContentTool import MessageContentTool

from utils import standard_result_parser

from dotenv import load_dotenv
load_dotenv()


def sales_agent(llm_obj, user_email, user_language="en") -> Agent:
    """
    Flexible Sales Agent that adapts to context and takes initiative
    """
    
    # Database connection
    connection = MongoDBConnection(
        connection_string=os.getenv("MONGO_DB_URI"),
        db_name=os.getenv("DB_NAME")
    )
    
    # All tools available
    list_collections_tool = MongoDBListCollectionsTool(connection)
    create_document_tool = MongoDBCreateDocumentTool(connection)
    create_bulk_document_tool = MongoDBBulkCreateTool(connection)
    update_document_tool = MongoDBUpdateDocumentTool(connection)
    delete_document_tool = MongoDBDeleteDocumentTool(connection)
    read_data_tool = MongoDBReadDataTool(connection)
    delete_bulk_document_tool = MongoDBBulkDeleteTool(connection)
    count_documents_tool = MongoDBCountDocumentsTool(connection, user_email)
    whatsapp_tool = WhatsAppTool(user_email=user_email)
    whatsapp_bulk_tool = WhatsAppBulkSenderTool(user_email=user_email)
    email_tool = MailerSendTool(user_email=user_email)
    content_tool = MessageContentTool(user_email=user_email)
    
    # Get collections info
    try:
        collections_info = list_collections_tool._run()
    except:
        collections_info = "Collections available: customers, deals, campaigns, messages"
    
    # Flexible and intelligent goal
    goal_text = f"""
    ROLE: Sales CRM Agent.

    Output language: {user_language}.
    DATA SCOPE: Filter ALL DB queries with {{'userEmail': {user_email}}}. Collections: {collections_info}. Use only these.

    CORE RULES
    1) Execute ONLY what the user (or assigned task step) explicitly requests.
    2) CRUD on customers/leads/deals exactly as asked.
    3) Search and retrieve data only when asked or when required to complete a requested action (e.g., to resolve a recipient).
    4) SEND WhatsApp/Email ONLY when the instruction literally includes sending (or when the manager’s task step says “send”).
    5) Keep confirmations brief.

    RESPONSE FORMAT
    - Add: "✅ تم إضافة name" / "✅ Added name"
    - Update/Delete: "✅ تم التحديث" / "✅ Updated" (or "✅ تم الحذف")
    - Search: return the data (minimal columns if large).
    - Errors: "❌ brief reason"

    FORBIDDEN
    - Creating campaigns unless explicitly requested.
    - Suggesting actions after SEND/CRUD. (Suggestions allowed after SEARCH/DRAFT only.)
    - Assuming intent or taking initiative beyond the instruction.
    - Messaging without explicit “send”.

    Always respond strictly in {user_language}.
    """

    backstory_text = f"""
    You are a disciplined Sales CRM AI Agent.
    You follow instructions word-for-word and never infer intent.
    You never send messages unless clearly instructed.
    Operate only within {{'userEmail': {user_email}}}.
    Language: {user_language}.
    """

    return Agent(
        name="FlexibleSalesAgent",
        role="Intelligent Sales & CRM Assistant",
        goal=goal_text,
        backstory=backstory_text,
        tools=[
            # Full toolkit available
            list_collections_tool,
            create_document_tool,
            read_data_tool,
            update_document_tool,
            delete_document_tool,
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
        max_iter=5,  # Allow more iterations for complex tasks
        memory=True,  # Remember context within the task
        result_parser=standard_result_parser,
    )

def handle_output(result):
    # Stop re-calling tools once a valid result is found
    if isinstance(result, dict) and result.get("status") == "success":
        print("✅ Task completed successfully, stopping agent loop.")
        return result["message"]
    return result
# Test scenarios showing flexibility
if __name__ == "__main__":
    from crewai import LLM
    
    print("🧪 Testing Flexible Sales Agent\n")
    
    test_scenarios = [
        {
            "prompt": "أضف محمد",
            "expected_behavior": "Adds Mohamed, might ask for phone/email, suggests next steps"
        },
        {
            "prompt": "How are my customers in Dubai?",
            "expected_behavior": "Fetches Dubai customers, shows stats, recent activities"
        },
        {
            "prompt": "Send a message to the new customer",
            "expected_behavior": "Finds the most recent customer, prepares appropriate message"
        },
        {
            "prompt": "What happened yesterday?",
            "expected_behavior": "Fetches yesterday's activities, new customers, deals"
        },
        {
            "prompt": "احذف آخر عميل",
            "expected_behavior": "Finds and deletes the most recent customer after confirmation"
        }
    ]
    
    # Initialize
    llm = LLM(
        model="gpt-3.5-turbo",
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.3,  # Bit more creative
        max_tokens=1000,  # More room for comprehensive responses
    )
    
    # Create agent
    agent = sales_agent(llm, user_email="test@example.com", user_language="ar")
    
    print("📊 Agent Configuration:")
    print(f"   Tools: {len(agent.tools)} tools available")
    print(f"   Memory: Enabled")
    print(f"   Max iterations: 5")
    print(f"   Approach: Flexible & Intelligent")
    
    print("\n💡 Example Behaviors:")
    for scenario in test_scenarios:
        print(f"\n   Input: '{scenario['prompt']}'")
        print(f"   Expected: {scenario['expected_behavior']}")
    
    print("\n✅ Flexible Sales Agent Ready!")
    print("This agent will:")
    print("- Fetch data proactively")
    print("- Understand context")
    print("- Complete tasks thoroughly")
    print("- Suggest next steps")
    print("- Be genuinely helpful")
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
    MongoDBCountDocumentsTool
)

# Communication tools
from Tools.whatsApp_tools import WhatsAppTool
from Tools.email_tools import MailerSendTool

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
    update_document_tool = MongoDBUpdateDocumentTool(connection)
    delete_document_tool = MongoDBDeleteDocumentTool(connection)
    read_data_tool = MongoDBReadDataTool(connection)
    count_documents_tool = MongoDBCountDocumentsTool(connection, user_email)
    whatsapp_tool = WhatsAppTool(user_email=user_email)
    email_tool = MailerSendTool(user_email=user_email)
    
    # Get collections info
    try:
        collections_info = list_collections_tool._run()
    except:
        collections_info = "Collections available: customers, deals, campaigns, messages"
    
    # Flexible and intelligent goal
    goal_text = f"""
                You are a Sales CRM Agent. Execute tasks efficiently and respond briefly in {user_language}.

                CORE RULES:
                1. Add/Update/Delete customers as requested
                2. Search and retrieve data when needed
                3. Only send messages when EXPLICITLY asked to send
                4. Respond with brief confirmations

                RESPONSE FORMAT:
                - For adds: "✅ تم إضافة [name]" or "✅ Added [name]"
                - For updates: "✅ تم التحديث" or "✅ Updated"
                - For searches: Show the data directly
                - For errors: "❌ [brief error]"

                DO NOT:
                - Create campaigns unless asked
                - Write welcome messages unless asked
                - Add extra suggestions unless asked

                Database: {collections_info}
                User scope: {user_email}
                Language: {user_language}
                """
    
    # Intelligent backstory
    backstory_text = f"""
    You are a Senior Sales AI with deep understanding of CRM operations and sales psychology.
    
    Your philosophy: "Anticipate needs, provide value, be genuinely helpful."
    
    You understand that users often:
    - Don't specify everything they need
    - Assume you remember context
    - Want quick, smart solutions
    - Appreciate proactive suggestions
    
    Your approach is:
    • INTELLIGENT: Read between the lines
    • PROACTIVE: Fetch data before being asked
    • COMPREHENSIVE: Complete tasks fully
    • CONTEXTUAL: Use conversation history wisely
    • HELPFUL: Suggest logical next steps
    
    Examples of your intelligence:
    - User mentions a name → You search for that customer
    - User asks about sales → You fetch recent metrics
    - User wants to message someone → You get their contact info
    - User seems frustrated → You provide solutions, not just data
    
    You've managed 100,000+ customer interactions and learned that being
    genuinely helpful beats being strictly literal every time.
    
    Language: Always respond in {user_language}
    Context: Use it wisely to provide better service
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
            email_tool
        ],
        allow_delegation=False,
        llm=llm_obj,
        verbose=True,
        max_iter=5,  # Allow more iterations for complex tasks
        memory=True,  # Remember context within the task
    )


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
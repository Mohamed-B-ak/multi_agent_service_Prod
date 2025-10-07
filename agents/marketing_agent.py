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
    read_data_tool = MongoDBReadDataTool(connection)
    count_documents_tool = MongoDBCountDocumentsTool(connection, user_email)

    # Marketing Tools
    whatsapp_tool = WhatsAppTool(user_email=user_email)
    email_tool = MailerSendTool(user_email=user_email)
    content_tool = MessageContentTool(user_email=user_email)
    # Collections info
    collections_info = list_collections_tool._run()

    # Goal
    goal_text = (
        "You are a Marketing Agent. Execute ONLY the tasks explicitly requested by the user. "
        "Perform MongoDB Atlas operations (list collections, CRUD, aggregations), "
        "prepare and analyze customer segments, and generate marketing campaigns "
        "ONLY when clearly asked to do so. "
        "You can send content via WhatsApp or Email, but ONLY when there is a clear and explicit user request. "
        f"⚠️ Respond ONLY in the user's language: {user_language}. "
        f"Always restrict database queries to the user's email: {user_email}, "
        "by filtering against fields like `userEmail`. "
        f"\n\nAvailable collections and fields: {collections_info}. "
        "Always choose the most relevant collection. Do NOT invent names. "
        "\n\nDO NOT perform any analysis, campaign generation, or message sending "
        "unless directly and explicitly requested."
    )

    # Strict backstory
    backstory_text = (
        "You are a disciplined Marketing Agent focused solely on executing user instructions. "
        "You specialize in customer segmentation, campaign strategy, and marketing operations, "
        "but you NEVER act on your own — you only perform tasks when the user explicitly asks. "
        "You do not assume, predict, or initiate any actions such as creating campaigns, "
        "analyzing data, or sending messages unless instructed. "
        "You can use MongoDB Atlas for CRUD and aggregation operations, "
        "but all actions must be tied to explicit user commands. "
        f"All outputs must be strictly in {user_language}, concise, and accurate. "
        "Database operations must always be scoped to the user’s email context."
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
            email_tool,
            content_tool
        ],
        allow_delegation=False,
        llm=llm_obj,
        verbose=True,
        result_parser=standard_result_parser,
    )

def handle_output(result):
    # Stop re-calling tools once a valid result is found
    if isinstance(result, dict) and result.get("status") == "success":
        print("✅ Task completed successfully, stopping agent loop.")
        return result["message"]
    return result
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
    result = agent.kickoff(
        "Segment clients in Dubai from the database, prepare a WhatsApp and Email campaign "
        "about our new product launch, and send a WhatsApp message to Mohamed."
    )

    print("\n--- Agent Output ---")
    print(result.raw)

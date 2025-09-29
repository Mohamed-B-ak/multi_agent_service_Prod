# Tools/siyadah_openai_tool.py
import os
from crewai.tools import BaseTool
import openai

class SiyadahHelperTool(BaseTool):
    name: str = "Siyadah Helper Tool"
    description: str = "Answers questions about Siyadah using the knowledge base and OpenAI LLM."

    def _run(self, question: str) -> str:

        import openai

        # 1️⃣ Set your OpenAI API key
        openai.api_key =os.getenv("OPENAI_API_KEY")

        # 2️⃣ Knowledge base about Siyadah
        knowledge = """
                    ** Platform Features & Guide **
                    1. Creating an Account
                    New users can easily get started:
                    Visit the homepage and click Login.
                    Then click Create Account.
                    Fill in all the required fields (e.g., name, email, password).
                    Click Create Account to complete registration.
                    2. Logging In
                    Returning users can access their account:
                    Click the Login button on the homepage.
                    Enter your email and password.
                    Click Login to enter your dashboard.
                    3. Dashboard Overview
                    After logging in, you are taken to the Dashboard—the central hub for all features.
                    3.1 Smart Chat – :brain: AI-Powered Operations
                    The Smart Chat is one of the most powerful features in Siyadah. It acts as an intelligent assistant where users can type commands or queries and the chatbot will perform actions across the platform.
                    Key Capabilities:
                    :mag: Data Operations:
                    Ask the chatbot to retrieve structured data such as:
                    All users with emails and phone numbers
                    Specific user records by name, email, or filters
                    Export, summarize, or analyze this data in chat
                    :busts_in_silhouette: User Management via Chat:
                    Add new users directly by typing a request (e.g., "Add user John with email john@example.com and phone number...")
                    Modify or delete users using natural language commands
                    Get summaries like “How many active users do we have?”
                    :loudspeaker: Campaign Automation:
                    Launch email campaigns by simply instructing the bot (e.g., "Send email to all users about product update")
                    Send WhatsApp campaigns to one or multiple users (as long as WhatsApp integration is set up in settings)
                    Manage templates and campaigns directly through conversation
                    :frame_with_picture: File and Image Handling:
                    Upload images or files from your local computer during chat
                    Ask the chatbot to analyze or use uploaded content
                    Use files as part of user onboarding or knowledge training
                    :gear: Advanced Operations:
                    Set up automations like reminders, follow-ups, or trigger events
                    Train the bot on new company knowledge or update knowledge base via chat
                    Interact with APIs or integrated tools through conversational commands
                    3.2 Settings – :gear: Personalization & Integration
                    Customize how your platform works for you.
                    Profile Management:
                    Edit personal and business info:
                    Name
                    Company Name
                    Phone Number
                    Email
                    Place of Residence
                    Notification Settings:
                    Enable/disable alerts for:
                    WhatsApp
                    Email
                    Missed Calls
                    External Integrations:
                    Connect with third-party tools:
                    Set Email sender and its API Key
                    Configure WhatsApp API
                    Add your Webhook URL:
                    https://345e154d-7a73-4a6b-a1f4-9e25aeb6225c-00-2he07kh0y0uhg.janeway.replit.dev/api/whatsapp/webhook
                    Set up HubSpot integration with your API Key for CRM sync
                    4. Customer Management – :bust_in_silhouette: User Database Control
                    Access and manage all your customer data in one place.
                    Add New Users:
                    Click the Add User button
                    Enter user details and click Add
                    View & Edit Users:
                    Browse the list of all users
                    Modify any user’s info (e.g., phone number, email)
                    Delete Users:
                    Quickly remove any user from the system with a click
                    5. Knowledge Base – :books: Smart Document Research
                    steps: 
                    1 - go to dashboard
                    2 - go to knowledge base 
                    3 - upload your file 
                    4 - save it 
                    Train your AI and retrieve knowledge from documents:
                    Upload a PDF file
                    The system will index and allow you to:
                    Search content
                    Ask the chatbot to extract answers
                    Use the content for customer support or onboarding
        """

        # 4️⃣ Construct the messages for the chat API
        messages = [
            {"role": "system", "content": "You are an expert in the Siyadah platform."},
            {"role": "user", "content": f"Use the following knowledge base to answer the question accurately. If the answer is not in the knowledge base, say you don't know.\n\nKnowledge Base:\n{knowledge}\n\nQuestion: {question}"}
        ]

        # 5️⃣ Call the OpenAI ChatCompletion API
        try:
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.3,
                max_tokens=500
            )

            answer = response.choices[0].message.content.strip()
            return answer
        except Exception as e:
            return f"❌ Error while querying OpenAI: {str(e)}"

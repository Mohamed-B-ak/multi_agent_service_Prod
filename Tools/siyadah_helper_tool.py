# Tools/siyadah_openai_tool.py
import os
from crewai.tools import BaseTool
import openai

class SiyadahHelperTool(BaseTool):
    name: str = "Siyadah OpenAI Tool"
    description: str = "Answers questions about Siyadah using the knowledge base and OpenAI LLM."

    def _run(self, question: str) -> str:

        import openai

        # 1️⃣ Set your OpenAI API key
        openai.api_key =os.getenv("OPENAI_API_KEY")

        # 2️⃣ Knowledge base about Siyadah
        knowledge = """
        # Siyadah Platform - User Guide
        ## 1. What is Siyadah?
        Siyadah is a multi-agent AI platform designed to automate business workflows. 
        It allows users to:
        - Compose and send emails.
        - Send WhatsApp messages.
        - Make scripted calls.
        - Generate Python code.
        - Perform CRUD operations on databases.
        ## 2. How to use the platform
        ### 2.1 Sending Emails
        - Use the email agent in the chat interface.
        - Start by typing your request, e.g., "Send an email to John about the report."
        - The agent can compose the email for you or send it directly if you confirm.
        ### 2.2 Sending WhatsApp Messages
        - Use the WhatsApp agent.
        - Type your message request, e.g., "Send a WhatsApp to Sarah."
        - The agent can draft or send messages after confirmation.
        ### 2.3 Creating Tasks
        - You can create a new task in the chat interface or via API.
        - Provide a clear description and any necessary details.
        ### 2.4 Generating Python Code
        - Use the code agent to generate clean Python scripts.
        - Example: "Create a Python script to fetch sales data from MongoDB."
        ### 2.5 Database Operations
        - The database agent can perform CRUD operations on MongoDB.
        - Example commands: "List all customers", "Update the phone number for Ahmed."
        ## 3. Best Practices
        - Always confirm sending actions (email, WhatsApp, calls) before execution.
        - Provide clear instructions for code generation.
        - Use context if needed to clarify ambiguous tasks.
        ## 4. Support
        - If you encounter issues, contact support at: support@siyadah-ai.com
        - Check the online documentation for more detailed guides.
        ## 5. Notes
        - The system supports multiple languages and can respond in the user’s preferred language.
        - Always phrase your prompts clearly for best results.
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

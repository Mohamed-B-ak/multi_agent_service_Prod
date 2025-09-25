import os
import time
import base64
import langid
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from pymongo import MongoClient
from crewai import Crew, Process, Task, LLM
from agents.caller_agent import caller_agent
from agents.code_agent import code_agent
from agents.content_agent import content_agent
from agents.db_agent import db_agent
from agents.email_sender_agent import email_agent
from agents.manager_agent import manager_agent
from agents.understanding_agent import understanding_agent
from agents.whatsApp_sender import whatsapp_agent
from agents.siyadah_helper_agent import siyadah_helper_agent
from agents.web_analyser_agent import web_analyser_agent
from agents.knowledge_enhanced_content_agent import knowledge_enhancer_agent
from agents.file_creation_agent import file_creation_agent
from agents.crm_agent import crm_agent
from agents.planner_agent import planner
from fastapi.responses import JSONResponse
from fastapi import Request, Response
from datetime import datetime
from customers_service.orchestrator import generate_reply
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

FOLDER_PATH = os.path.join(os.getcwd(), "files")  
os.makedirs(FOLDER_PATH, exist_ok=True)


app = FastAPI()


def get_llm():
    """
    Initialize the LLM (Large Language Model) with a predefined model and API key.
    """
    return LLM(
        model="gpt-4o",
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.1,
        max_tokens=500,

    )
from typing import Optional

class UserPromptRequest(BaseModel):
    prompt: str
    user_email: str #Optional[str] = None   
    context: list = []   

def get_workers(user_email, user_language, knowledge_base, context_window=[]):
    """
    Initialize and return all worker agents.
    """
    llm_obj = get_llm()
    return [
        understanding_agent(llm_obj, user_language, context_window),
        content_agent(llm_obj, user_language),
        email_agent(llm_obj, user_email, user_language),
        whatsapp_agent(llm_obj, user_email, user_language),
        caller_agent(llm_obj, user_language),
        db_agent(llm_obj, user_email, user_language),
        siyadah_helper_agent(llm_obj, user_language),
        knowledge_enhancer_agent(llm_obj, knowledge_base, user_language),
        file_creation_agent(llm_obj),
        crm_agent(llm_obj, user_email, user_language),
    ]

from crewai import Task

from crewai import Task

def get_understand_and_execute_task():
    """
    Define and return the task for understanding and executing user prompts,
    with strict enforcement that no mock or dummy data (like example.com) is ever used.
    All recipient data must come directly from the Database Agent.
    """

    return Task(
        description=(
            "You manage an AI communication system capable of:\n"
            "1. 📧 **Email Content**: Draft professional emails using Content Specialist + Content Enhancement Agent.\n"
            "2. 📤 **Send Email**: Only with explicit request and after passing content to Content Enhancement Agent "
            "(make sure that the content doesn't contain placeholders).\n"
            "3. 📱 **WhatsApp Content**: Draft messages using Content Specialist + Content Enhancement Agent.\n"
            "4. 📲 **Send WhatsApp**: Only with explicit request while passing content through Content Enhancement Agent "
            "(make sure that the content doesn't contain placeholders).\n"
            "5. ☎️ **Call Scripts**: Initial script from Content Specialist + improvement via Content Enhancement Agent.\n"
            "6. ☎️ **Make Call**: Only after confirmation.\n"
            "7. 🗂️ **Database Operations (MongoDB)**: Execute CRUD (add, update, delete, query) restricted by user email {user_email}.\n"
            "8. 📄 **Create PDF, Word or Excel Files**: Using File Creator Agent and saving output in 'files/' folder.\n"
            "9. 🏢 **CRM Management (HubSpot, Salesforce, Zoho, ...)**: Role limited only to *extracting or displaying customer data* upon user authorization.\n"
            "10. 🤖 **Siyadah Questions and Inquiries**: Pass them to Siyadah Intelligent Agent.\n\n"

            "🧠 Context Usage Policy (internal only):\n"
            "- {context_window} can be used to understand the prompt , get some informations (whatsApp or email content or contacts(phone number or mail address) ) "
            "and complete missing information when needed, without displaying summaries or context references.\n"
            "- Use the context window to understand what the user means.\n"
            "- Explicit user request has priority if it conflicts with context.\n\n"

            "📝 Strict Concision Mode:\n"
            "- Answer only what's asked without additions.\n"
            "- Yes/No answered briefly.\n\n"

            "User Request : \n\n {user_prompt}\n\n"

            "📌 Smart Routing:\n"
            "📧 intent = 'draft email' → Content Specialist + Content Enhancement Agent\n"
            "📧 intent = 'send email' → (Content Specialist + Content Enhancement Agent if no content already generated in the context window ) "
            "+ Database Specialist (to fetch recipients) + Email Specialist\n"
            "📱 intent = 'draft whatsapp' → Content Specialist + Content Enhancement Agent\n"
            "📱 intent = 'send whatsapp' → (Content Specialist + Content Enhancement Agent if no content already generated in the context window ) "
            "+ Database Specialist (to fetch recipients) + WhatsApp Specialist\n"
            "☎️ intent = 'draft call' → Content Specialist + Content Enhancement Agent\n"
            "☎️ intent = 'make call' → Content Specialist + Content Enhancement Agent + Call Specialist\n"
            "🗂️ intent = 'database operations' (add/update/delete/query) → Database Specialist\n"
            "📝 intent = 'create PDF, Word or Excel file' → File Creator Agent\n"
            "🏢 intent = 'CRM' → Invoke CRM Agent only to extract/display customer data (Only with explicit request).\n"
            "❓ intent = 'inquiry' or 'help' → Siyadah Intelligent Agent\n"
            "🔄 multiple intents → Coordinate between agents\n"
            "❓ unclear intent or missing data → Smart clarification with direct question before execution.\n\n"

            "📜 Execution Protocol:\n"
            "1. Detect user language.\n"
            "2. Analyze intent using Understanding Agent.\n"
            "3. Respond in same user language.\n"
            "4. In *drafting*: Generate content then enhance.\n"
            "5. In *sending*: Verify message type, channel, and recipients → "
            "⚠️ CRITICAL: Always query the Database Specialist for real customer emails/phone numbers before sending. "
            "NEVER use placeholders, dummy data, or example.com.\n"
            "6. In *database*: All add, update, and delete operations execute on internal DB only.\n"
            "7. In *files*: Create file via File Creator Agent and save in 'files/' folder.\n"
            "8. In *CRM management*: Only allow query/extraction.\n"
            "9. In Siyadah inquiries: Pass to Knowledge Agent.\n"
            "10. Direct questions: Concise answer.\n"
            "11. In case of ambiguous intent or missing data: Ask clarification question before any execution.\n"
            "12. Confirmation only for executive commands.\n"
            "13. Handle errors with polite and brief language.\n\n"

            "🚨 Safety Procedures:\n"
            "- For ALL send requests (email or WhatsApp): "
            "recipients MUST come from Database Specialist (customers/clients collection).\n"
            "- If no real recipients are found, STOP and ask the user. "
            "Do not fallback to dummy addresses (like client@example.com).\n"
            "- No sending or execution except with clear and explicit request.\n"
            "- All CRUD operations occur on internal database only.\n"
            "- CRM used exclusively for displaying/extracting customer data.\n"
            "- No action executed with ambiguous intent or missing data except after user clarification.\n"
            "- Verify email and sending destination.\n"
            "- Professionalism required in all responses.\n"
            "- Always verify database operations are restricted by user email.\n"
        ),
        expected_output=(
            "Concise outputs based on intent:\n"
            "✅ Yes/No: Short answer.\n"
            "✅ Drafting: Text only.\n"
            "✅ Sending: Brief confirmation with text when needed, showing the REAL recipient(s) from DB.\n"
            "✅ Database: CRUD result linked to user email with confirmation text.\n"
            "✅ PDF/Word/Excel files: Confirmation message with file path in 'files/' folder.\n"
            "✅ CRM Management: Display or extract customer data only upon user authorization.\n"
            "✅ Siyadah inquiries: Accurate response from knowledge base.\n"
            "✅ Clarification: Direct question to determine intent or provide missing data.\n"
            "⚠️ No summaries or additional comments except by user request.\n"
            "🔣 Response language = {user_language}.\n\n"
            "**Success Criteria for Digital Tasks:**\n"
            "- All recipients are fetched from DB, never mocked.\n"
            "- Confirmation text includes the actual recipient(s).\n"
            "- When this format is achieved, task is considered complete"
        ),
    )




def detect_language(text: str) -> str:
    langid.set_languages(['fr', 'en', 'ar'])
    lang, _ = langid.classify(text)
    print(lang)
    return lang  

@app.post("/process-prompt/")
async def process_prompt(request: UserPromptRequest):
    """
    FastAPI endpoint that:
    1. Runs the agent and gets final result.
    2. If a file exists in ./files → include it (base64) in the response.
    3. Deletes the file after including it.
    """
    user_prompt = request.prompt
    context_window = request.context
    user_email = request.user_email #"mohamed.ak@d10.sa"
    llm_obj = get_llm()
    
    try:
        user_language = detect_language(user_prompt)
    except Exception:
        user_language = "en"
    mgr = manager_agent(llm_obj, user_language)

    try:
        client = MongoClient(os.getenv("MONGO_DB_URI"))
        db = client[os.getenv("DB_NAME")]
        collection = db["knowledgebases"]
        user_doc = collection.find_one({"userId": user_email})
        knowledge_base = user_doc['extractedContent']
    except:
        knowledge_base = ""

    workers = get_workers(user_email, user_language, knowledge_base, context_window)
    understand_and_execute = get_understand_and_execute_task()

    tasks = planner(user_prompt, context_window, llm_obj)

    crew = Crew(
        agents=workers,
        tasks=[understand_and_execute],
        process=Process.hierarchical,
        manager_agent=mgr,
        verbose=True,
    )

    start = time.time()
    try:
        final = crew.kickoff(inputs={
            "user_prompt": tasks,
            "context_window": context_window,
            "user_email": user_email,
            "user_language": user_language
        })

        if hasattr(final, "raw"):
            final_output = final.raw
        elif isinstance(final, dict) and "raw" in final:
            final_output = final["raw"]
        else:
            final_output = str(final)

        execution_time = time.time() - start
        print(execution_time)

        file_data = None
        file_name = None

        if os.path.exists(FOLDER_PATH):
            files = os.listdir(FOLDER_PATH)
            if files:  
                file_path = os.path.join(FOLDER_PATH, files[0])
                file_name = files[0]


                with open(file_path, "rb") as f:
                    file_data = base64.b64encode(f.read()).decode("utf-8")

                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Could not delete {file_path}: {e}")


        return JSONResponse(content={
            "final_output": final_output,
            "execution_time": execution_time,
            "file_name": file_name,
            "file_content": file_data 
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred: {str(e)}")



@app.post("/webhook/")
async def webhook_listener(request: Request):
    """
    Webhook endpoint for receiving external events (WhatsApp, Email).
    Processes message, generates reply with agents, and sends it back.
    """
    from customers_service.orchestrator import generate_reply
    try:
        payload = await request.json()
        headers = dict(request.headers)
        print(payload)
        # Detect channel & extract message
        if "from" in payload and payload.get("event") == "onmessage":
            channel = "whatsApp"
            customer_number = payload.get("from")
            customer_message = payload.get("body")
            session = payload.get("session")
            time = datetime.utcnow(),
            #TODO save the comming message    
            client = MongoClient(os.getenv("MONGO_DB_URI"))
            db = client[os.getenv("DB_NAME")]
            usercredentials = db["usercredentials"]
            doc = usercredentials.find_one({"whatsapp.sessionName": session})
            if doc:
                user_email = doc.get("userEmail")
            else:
                user_email = None
            print(user_email)
            user_email = "mohamed.ak@d10.sa"
            #TODO getting the context
            print("customer_number")
            print(customer_number)
            print("customer_message")
            print(customer_message)
            print("user_email")
            print(user_email)
            print("time")
            print(time)
            clean_number = "+" + customer_number.replace("@c.us", "")
            try:
                emails_collection = db["whatsappmessages"]  
        
                new_message = {"user": customer_message}

                # Vérifier si une conversation existe déjà
                existing_conversation = emails_collection.find_one({
                    "user_email": user_email,
                    "to_number": clean_number
                })

                if existing_conversation:
                    # Mettre à jour la conversation existante
                    emails_collection.update_one(
                        {"_id": existing_conversation["_id"]},
                        {
                            "$push": {"messages": new_message},
                            "$set": {"time": datetime.utcnow()}
                        }
                    )
                else:
                    # Créer une nouvelle conversation
                    emails_collection.insert_one({
                        "user_email": user_email,
                        "to_number": clean_number,
                        "time": datetime.utcnow(),
                        "messages": [new_message]
                    })
            except Exception as e:
                    print("failed to save the comming whatsApp message ")
            try : 
                conversation = emails_collection.find_one({
                    "user_email": user_email,
                    "to_number": clean_number
                })

                if conversation and "messages" in conversation:
                    # Prendre les 8 derniers messages
                    last_messages = conversation["messages"][-8:]
                    for msg in last_messages:
                        print(msg)
                    history = last_messages
                else:
                    print("Aucune conversation trouvée")
                    history = []
            except:
                history = []
            generate_reply(customer_number, channel="whatsApp", message= customer_message, user_email=user_email, history=history)
            
            return Response(status_code=200)
            #customer_id, channel, message = await handlers.handle_whatsapp(payload)
        #elif "recipient" in payload:
            #customer_id, channel, message = await handlers.handle_email(payload)
        else:
            # Unknown webhook source, just ack
            return Response(status_code=200)

        print(f"📥 Incoming {channel} message from {customer_id}: {message}")

        # Save incoming customer message
        db.save_message(customer_id, channel, "customer", message)

        # Get full conversation history
        history = db.get_conversation(customer_id)

        # Generate reply with multi-agent system
        reply = await orchestrator.generate_reply(customer_id, channel, message, history)

        # Save agent reply to DB
        db.save_message(customer_id, channel, "agent", reply)

        # Send reply via the correct agent
        if channel == "whatsapp":
            llm_obj = get_llm()
            wa = whatsapp_agent(llm_obj, customer_id, "auto")
            wa.send_message(customer_id, reply)
            print(f"📤 Sent WhatsApp reply to {customer_id}: {reply}")

        elif channel == "email":
            llm_obj = get_llm()
            em = email_agent(llm_obj, customer_id, "auto")
            em.send_email(customer_id, "Customer Support", reply)
            print(f"📤 Sent Email reply to {customer_id}: {reply}")

        # Always acknowledge webhook
        return Response(status_code=200)

    except Exception as e:
        print(f"❌ Webhook error: {e}")
        return Response(status_code=400)

@app.get("/")
async def get_chat_interface():
    """
    Serve the HTML interface for the chat.
    """
    html_file_path = os.path.join(os.path.dirname(__file__), "index.html")
    
    # Check if the file exists
    if os.path.exists(html_file_path):
        with open(html_file_path, "r") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    else:
        raise HTTPException(status_code=404, detail="HTML chat interface not found.")
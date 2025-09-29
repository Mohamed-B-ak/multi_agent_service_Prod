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
from agents.db_agent import db_agent
from agents.email_sender_agent import email_agent
from agents.manager_agent import manager_agent
from agents.whatsApp_sender import whatsapp_agent
from agents.siyadah_helper_agent import siyadah_helper_agent
from agents.file_creation_agent import file_creation_agent
from agents.crm_agent import crm_agent
from agents.planner_agent import planner
from agents.knowledge_based_content_agent import knowledge_based_content_agent
from fastapi.responses import JSONResponse
from fastapi import Request, Response
from datetime import datetime
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
        email_agent(llm_obj, user_email, user_language),
        whatsapp_agent(llm_obj, user_email, user_language),
        caller_agent(llm_obj, user_language),
        db_agent(llm_obj, user_email, user_language),
        siyadah_helper_agent(llm_obj, user_language),
        file_creation_agent(llm_obj),
        knowledge_based_content_agent(llm_obj, knowledge_base, user_language),
    ]

from crewai import Task

from crewai import Task

def get_understand_and_execute_task():
    """
    Define and return the task for understanding and executing user prompts,
    with strict enforcement that no mock or dummy data (like example.com) is ever used.
    All recipient data must come directly from the Database Agent.
    Content creation is done by the unified Knowledge-Based Content Agent.
    """

    return Task(
        description=(
            "You manage an AI communication system capable of:\n"
            "1. 📧 **Email Content**: Draft professional emails using Knowledge-Based Content Agent (no placeholders, enriched with company knowledge).\n"
            "2. 📤 **Send Email**: Only with explicit request after content is created without placeholders.\n"
            "3. 📱 **WhatsApp Content**: Draft messages using Knowledge-Based Content Agent (no placeholders, knowledge-enriched).\n"
            "4. 📲 **Send WhatsApp**: Only with explicit request after content is verified to have no placeholders.\n"
            "5. ☎️ **Call Scripts**: Create scripts using Knowledge-Based Content Agent (natural language, no templates).\n"
            "6. ☎️ **Make Call**: Only after confirmation.\n"
            "7. 🗂️ **Database Operations (MongoDB)**: Execute CRUD (add, update, delete, query) restricted by user email {user_email} using th db_agent .\n"
            "8. 📄 **Create PDF, Word or Excel Files**: Using File Creator Agent and saving output in 'files/' folder.\n"
            "9. 🤖 **Siyadah Questions and Inquiries**: Pass them to Siyadah Intelligent Agent.\n\n"

            "⭐ **Knowledge-Based Content Agent Capabilities**:\n"
            "- Creates content directly from company knowledge base\n"
            "- NEVER uses placeholders like name, company, etc.\n"
            "- Automatically adapts tone and format for each channel\n"
            "- Produces immediately sendable content without post-processing\n\n"

            "🧠 Context Usage Policy (internal only):\n"
            "- {context_window} can be used to understand the prompt, get information (WhatsApp or email content or contacts) "
            "and complete missing information when needed, without displaying summaries or context references.\n"
            "- Use the context window to understand what the user means.\n"
            "- Explicit user request has priority if it conflicts with context.\n\n"

            "📝 Strict Concision Mode:\n"
            "- Answer only what's asked without additions.\n"
            "- Yes/No answered briefly.\n\n"
            "the user prompt can a simple prompt or question and it can be a list of tasks "
            "User Request: \n\n {user_prompt}\n\n"

            "📌 Smart Routing (Simplified with Combined Agent):\n"
            "📧 intent = 'draft email' → Knowledge-Based Content Agent\n"
            "📧 intent = 'send email' → Knowledge-Based Content Agent (if no content in context) + Database Specialist (recipients) + Email Specialist\n"
            "📱 intent = 'draft whatsapp' → Knowledge-Based Content Agent\n"
            "📱 intent = 'send whatsapp' → Knowledge-Based Content Agent (if no content in context) + Database Specialist (recipients) + WhatsApp Specialist\n"
            "☎️ intent = 'draft call' → Knowledge-Based Content Agent\n"
            "☎️ intent = 'make call' → Knowledge-Based Content Agent + Call Specialist\n"
            "🗂️ intent = 'database operations' → Database Specialist\n"
            "📝 intent = 'create file' → File Creator Agent\n"
            "❓ intent = 'inquiry/help' → Siyadah Intelligent Agent\n"
            "🔄 multiple intents → Coordinate between agents\n"
            "❓ unclear intent → Clarification question\n\n"

            "📜 Execution Protocol (Streamlined):\n"
            "1. Analyze intent from the user request.\n"
            "2. Respond in same user language.\n"
            "3. **Content Creation**: Knowledge-Based Content Agent creates final content in ONE step (no enhancement needed).\n"
            "4. **Sending Verification**:\n"
            "   - Confirm content has NO placeholders\n"
            "   - Query Database Specialist for REAL recipients\n"
            "   - NEVER use dummy data or example.com\n"
            "5. **Database**: Execute CRUD on internal DB only.\n"
            "6. **Files**: Create and save in 'files/' folder.\n"
            "7. **Siyadah**: Route to Knowledge Agent.\n"
            "8. **Direct Questions**: Concise answer.\n"
            "9. **Missing Data**: Ask for clarification.\n"
            "10. **Confirmations**: Only for executive commands.\n"
            "11. **Errors**: Handle politely and briefly.\n\n"

            "🚨 Critical Safety Rules:\n"
            "- **Content Quality**: Knowledge-Based Content Agent ensures NO placeholders ever appear\n"
            "- **Recipients**: MUST come from Database Specialist (never mocked)\n"
            "- **Sending**: Only with explicit request and real recipients\n"
            "- **No Fallbacks**: If recipients not found, STOP and ask user\n"
            "- **Database Scope**: All operations restricted by user email\n"
            "- **Professional Standards**: All responses must be professional\n"
            "- **Language Consistency**: Always respond in {user_language}\n"
        ),
        expected_output=(
            "Concise outputs based on intent:\n"
            "✅ Yes/No: Short answer.\n"
            "✅ Drafting: Final content only (no placeholders, knowledge-enriched).\n"
            "✅ Sending: Confirmation with REAL recipients from DB.\n"
            "✅ Database: CRUD result with user email confirmation.\n"
            "✅ Files: Confirmation with path in 'files/' folder.\n"
            "✅ Siyadah: Knowledge base response.\n"
            "✅ Clarification: Direct question for missing info.\n"
            "⚠️ No summaries unless requested.\n"
            "🔣 Response language = {user_language}.\n\n"
            "**Success Criteria:**\n"
            "- Content is placeholder-free and knowledge-based\n"
            "- Recipients are real (from DB)\n"
            "- Confirmations include actual recipients\n"
            "- Task complete when format achieved"
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
    user_email = request.user_email
    llm_obj = get_llm()
    
    from utils import save_message, get_messages
     # Save user input

    save_message(user_email, "user", user_prompt)

    # Get chat history

    redis_context_window = get_messages(user_email, limit=10)

    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print(redis_context_window)
    print(type(redis_context_window))
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++")
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

    workers = get_workers(user_email, user_language, knowledge_base, str(redis_context_window))
    understand_and_execute = get_understand_and_execute_task()

    tasks = planner(user_prompt, str(redis_context_window), llm_obj)
    print(tasks)
    print(type(tasks))
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
            "context_window": str(redis_context_window),
            "user_email": user_email,
            "user_language": user_language
        })

        if hasattr(final, "raw"):
            final_output = final.raw
        elif isinstance(final, dict) and "raw" in final:
            final_output = final["raw"]
        else:
            final_output = str(final)
        # Save system response
        try : 
            save_message(user_email, "system", final_output)
        except:
            print("Sorry, i can't save the system response")
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
        print(e)
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
                return Response("i can't find the user email related to this customer ",status_code=400)
            print(user_email)
            
            #TODO getting the context
            print("customer_number")
            print(customer_number)
            print("customer_message")
            print(customer_message)
            print("user_email")
            print(user_email)
            print("time")
            print(time)
            clean_number = customer_number.replace("@c.us", "")  # Remove @c.us
            if not clean_number.startswith("+"):
                clean_number = "+" + clean_number  # Add + if missing
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
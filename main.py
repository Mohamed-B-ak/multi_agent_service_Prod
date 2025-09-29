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
from agents.sales_agent import sales_agent
from agents.marketing_agent import marketing_agent
from fastapi.responses import JSONResponse
from fastapi import Request, Response
from datetime import datetime
import warnings
import redis 
warnings.filterwarnings("ignore", category=DeprecationWarning)

FOLDER_PATH = os.path.join(os.getcwd(), "files")  
os.makedirs(FOLDER_PATH, exist_ok=True)


app = FastAPI()

mongo_client = None
db = None
redis_client= None


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
    user_email: Optional[str] = None   
    context: list = []   

def get_workers(user_email, user_language, knowledge_base, context_window=[]):
    """
    Initialize and return all worker agents.
    """
    llm_obj = get_llm()
    return [
        marketing_agent(llm_obj, user_language),
        sales_agent(llm_obj, user_language),
        siyadah_helper_agent(llm_obj, user_language),
    ]

from crewai import Task

from crewai import Task
def get_understand_and_execute_task():
    """
    Define and return the task for understanding and executing user prompts,
    optimized for Marketing, Sales, and Siyadah Helper agents only.
    """

    return Task(
        description=(
            "You manage an AI system with THREE specialized agents capable of:\n\n"
            
            "🎯 **MARKETING AGENT Capabilities**:\n"
            "1. 📊 **Campaign Management**: Create and execute multi-channel marketing campaigns\n"
            "2. 📧 **Email Marketing**: Draft and send marketing emails via MailerSend\n"
            "3. 📱 **WhatsApp Campaigns**: Create and send WhatsApp marketing messages\n"
            "4. 🗂️ **Customer Segmentation**: Query and segment customers from MongoDB\n"
            "5. 📈 **Analytics**: Analyze campaign performance and customer engagement\n"
            "6. 🎨 **Content Creation**: Generate marketing content enriched with knowledge base\n"
            "7. 🔍 **Database Operations**: CRUD operations on MongoDB (customers, campaigns, etc.)\n\n"
            
            "💼 **SALES AGENT Capabilities**:\n"
            "1. 🤝 **Lead Management**: Track and nurture leads through the sales funnel\n"
            "2. 📞 **Sales Outreach**: Create personalized sales pitches and follow-ups\n"
            "3. 💰 **Deal Tracking**: Monitor and update sales opportunities in database\n"
            "4. 📊 **CRM Operations**: Manage customer relationships and sales data\n"
            "5. 📧 **Sales Emails**: Send targeted sales emails with product information\n"
            "6. 📱 **WhatsApp Sales**: Direct sales messaging to prospects\n"
            "7. 🗂️ **Database Management**: Access and update sales records in MongoDB\n\n"
            
            "❓ **SIYADAH HELPER AGENT Capabilities**:\n"
            "1. 📚 **Platform Knowledge**: Answer questions about Siyadah platform\n"
            "2. 🔧 **Technical Support**: Help with platform features and troubleshooting\n"
            "3. 📖 **User Guidance**: Provide instructions on how to use the system\n"
            "4. 💡 **Best Practices**: Share tips for effective platform usage\n"
            "5. 🎓 **Training**: Explain agent capabilities and workflows\n\n"
            
            "🧠 **Context Usage Policy**:\n"
            "- {context_window} helps understand user intent and previous interactions\n"
            "- Use context to maintain conversation continuity\n"
            "- User's explicit request overrides context if conflicting\n\n"
            
            "📝 **Communication Principles**:\n"
            "- Respond in {user_language} consistently\n"
            "- Keep responses concise and action-oriented\n"
            "- No placeholders or dummy data - use real information only\n\n"
            
            "User Request: \n\n {user_prompt}\n\n"
            
            "📌 **Smart Agent Routing**:\n"
            "🎯 'marketing campaign', 'email blast', 'customer segment' → **Marketing Agent**\n"
            "💼 'sales', 'leads', 'deals', 'prospects', 'close' → **Sales Agent**\n"
            "❓ 'how to', 'help', 'what is Siyadah', 'platform question' → **Siyadah Helper Agent**\n"
            "🔄 Multiple needs → Coordinate between relevant agents\n"
            "❓ Unclear intent → Ask for clarification\n\n"
            
            "📜 **Execution Protocol**:\n"
            "1. **Intent Analysis**: Determine which agent(s) should handle the request\n"
            "2. **Language Detection**: Ensure response matches user's language\n"
            "3. **Context Integration**: Use previous conversation for continuity\n"
            "4. **Agent Selection**:\n"
            "   - Marketing tasks → Marketing Agent\n"
            "   - Sales tasks → Sales Agent\n"
            "   - Platform questions → Siyadah Helper Agent\n"
            "   - Complex tasks → Multiple agents in sequence\n"
            "5. **Data Validation**:\n"
            "   - All database queries scoped by {user_email}\n"
            "   - Real customer data only (no mocks)\n"
            "   - Verify credentials before sending messages\n"
            "6. **Quality Control**:\n"
            "   - No placeholders in content\n"
            "   - Professional tone maintained\n"
            "   - Clear, actionable responses\n"
            "7. **Error Handling**:\n"
            "   - Missing data → Request clarification\n"
            "   - Failed operations → Clear error message\n"
            "   - No credentials → Inform user to add them\n\n"
            
            "⚡ **Performance Optimizations**:\n"
            "- Both Marketing and Sales agents have MongoDB tools - use efficiently\n"
            "- Both can send WhatsApp/Email - choose based on context\n"
            "- Share customer data between agents to avoid duplicate queries\n"
            "- Cache frequently accessed data\n\n"
            
            
            "🚨 **Critical Rules**:\n"
            "- **Data Security**: All operations restricted to user's data only\n"
            "- **Real Data Only**: Never use example.com or dummy numbers\n"
            "- **Credential Check**: Verify API keys exist before sending\n"
            "- **Rate Limiting**: Respect API limits for email/WhatsApp\n"
            "- **Professional Standards**: Maintain business communication quality\n"
            "- **Language Consistency**: Always respond in {user_language}\n"
        ),
        expected_output=(
            "Expected outputs by agent type:\n\n"
            "🎯 **Marketing Agent Outputs**:\n"
            "✅ Campaign created with [X] recipients targeted\n"
            "✅ Email sent to [X] customers about [campaign]\n"
            "✅ WhatsApp blast queued for [X] contacts\n"
            "✅ Customer segment: [X] customers match criteria\n"
            "✅ Content drafted: [actual marketing content]\n\n"
            
            "💼 **Sales Agent Outputs**:\n"
            "✅ Lead added/updated: [customer name] - [status]\n"
            "✅ Sales email sent to [prospect name] at [email]\n"
            "✅ [X] prospects identified for [product/service]\n"
            "✅ Deal updated: [deal name] moved to [stage]\n"
            "✅ Follow-up scheduled for [X] leads\n\n"
            
            "❓ **Siyadah Helper Outputs**:\n"
            "✅ Clear explanation of requested feature\n"
            "✅ Step-by-step instructions provided\n"
            "✅ Best practice recommendation given\n"
            "✅ Platform capability clarified\n\n"
            
            "📊 **General Format Rules**:\n"
            "🔣 Response language = {user_language}\n"
            "📝 Concise, actionable responses\n"
            "🎯 Include specific numbers and names\n"
            "⚠️ No summaries unless requested\n"
            "✔️ Confirm completion with details\n"
            "➕ Always end with a context-aware recommendation question\n"
        ),
    )
def detect_language(text: str) -> str:
    langid.set_languages(['fr', 'en', 'ar'])
    lang, _ = langid.classify(text)
    print(lang)
    return lang  

@app.on_event("startup")
async def startup_event():
    global mongo_client, db, redis_client
    mongo_client = MongoClient(os.getenv("MONGO_DB_URI"))
    db = mongo_client[os.getenv("DB_NAME")]
   
    redis_client = redis.from_url(
        os.getenv("REDIS_URL"),
        decode_responses=True
    )

    print("success")


@app.post("/process-prompt/")
async def process_prompt(request: UserPromptRequest):
    """
    FastAPI endpoint that:
    1. Runs the agent and gets final result.
    2. If a file exists in ./files → include it (base64) in the response.
    3. Deletes the file after including it.
    """
    start = time.time()
    user_prompt = request.prompt
    context_window = request.context
    user_email = "mohamed.ak@d10.sa"
    llm_obj = get_llm()
    
    from utils import save_message, get_messages
    # Save user input

    save_message(redis_client, user_email, "user", user_prompt)

    # Get chat history

    redis_context_window = get_messages(redis_client, user_email, limit=10)

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
        #client = MongoClient(os.getenv("MONGO_DB_URI"))
        #db = client[os.getenv("DB_NAME")]
        collection = db["knowledgebases"]
        user_doc = collection.find_one({"userId": user_email})
        knowledge_base = user_doc['extractedContent']
    except:
        knowledge_base = ""
    execution_time = time.time() - start
    print("-----------------------")
    print(execution_time)
    print("-----------------------")
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
            save_message(redis_client, user_email, "system", final_output)
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
            #client = MongoClient(os.getenv("MONGO_DB_URI"))
            #db = client[os.getenv("DB_NAME")]
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
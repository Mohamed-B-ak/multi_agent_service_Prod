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
from agents.customer_service_agent import customer_service_agent
from fastapi.responses import JSONResponse
from fastapi import Request, Response
from datetime import datetime
import warnings
import redis 
warnings.filterwarnings("ignore", category=DeprecationWarning)

FOLDER_PATH = os.path.join(os.getcwd(), "files")  
os.makedirs(FOLDER_PATH, exist_ok=True)


app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

origins = [
    "https://multi-agent-whbj.onrender.com",  # your frontend
    "http://localhost:8000",                  # local dev
    "http://127.0.0.1:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,   # Or ["*"] to allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

mongo_client = None
db = None
redis_client= None



def get_llm():
    """
    Initialize the LLM (Large Language Model) with a predefined model and API key.
    """
    return LLM(
        model="gpt-3.5-turbo",
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.1,
        max_tokens=500,

    ), LLM(
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

def clean_agent_output(output: str, language: str = "ar") -> str:
    """Clean up malformed agent outputs"""
    
    # Remove incomplete thoughts
    if "Thought:" in output or "Action:" in output or output.strip().endswith(":"):
        if language == "ar":
            return "✅ تمت العملية بنجاح"
        return "✅ Operation completed successfully"
    
    # Remove placeholders
    output = output.replace("[Your Name]", "فريق المبيعات")
    output = output.replace("[Your Position]", "")
    output = output.replace("[Your Company]", "")
    
    # Remove any markdown artifacts
    output = output.replace("```", "").strip()
    
    return output

def get_workers(user_email, user_language, knowledge_base, selected_agents, context_window=[]):
    """
    Initialize and return all worker agents.
    """
    llm_obj, _ = get_llm()
    selected_worker = []
    if isinstance(selected_agents, list) and len(selected_agents) > 0 : 
        if "marketing_agent" in selected_agents : 
            selected_worker.append(marketing_agent(llm_obj, user_email,  user_language))
        if "sales_agent" in selected_agents: 
            selected_worker.append(sales_agent(llm_obj, user_email, user_language))
        if "data_agent" in  selected_agents : 
            selected_worker.append(db_agent(llm_obj, user_email, user_language))
        
    else : 
        return [
            marketing_agent(llm_obj, user_email,  user_language),
            sales_agent(llm_obj, user_email, user_language),
            db_agent(llm_obj, user_email, user_language)
        ]
    return selected_worker
from crewai import Task

from crewai import Task
def get_understand_and_execute_task(
    user_prompt,
    user_email,
    user_language,
    dialect,
    tone,
    urgency,
    selected_agents=None,  # list or None
    context_window="",
):
    """
    Build ONE Task that integrates multiple Siyadah specialized agents if needed.
    Always returns a single Task object.

    Rule:
    - If selected_agents is None or empty, include ALL agents.
    """

    # 🧩 Define agent-specific profiles
    agent_profiles = {
        "marketing_agent": """
        🎯 **MARKETING AGENT**
        - Focus: audience-wide communication, campaigns, promotions, and general engagement.
        - Channels: WhatsApp, Email, social media.
        - Capabilities:
            1. 📊 Campaign Management (multi-channel)
            2. 🎨 Content Creation and Personalization
            3. 📧 Email + WhatsApp Messaging
            4. 🗂️ Customer Segmentation (via database queries)
            5. 📈 Marketing Analytics (clicks, opens, engagement)
        """,

        "sales_agent": """
        💼 **SALES AGENT**
        - Focus: lead nurturing, follow-ups, deals, offers, and conversions.
        - Channels: WhatsApp, Email, CRM.
        - Capabilities:
            1. 🤝 Lead Management and Follow-ups
            2. 💬 Personalized WhatsApp/Email Outreach
            3. 💰 Deal Tracking and Pipeline Updates
            4. 📊 CRM Operations (retrieve/update lead data)
            5. 🔍 Post-Campaign Follow-ups
        """,

        "data_agent": """
        🗂️ **DATA AGENT**
        - Focus: database operations, reports, and structured data queries.
        - Capabilities:
            1. 📦 CRUD operations (create, read, update, delete)
            2. 📋 Data validation and consistency checks
            3. 📈 Generate structured client reports
            4. 🔍 Handle customer records and analytics datasets
        """,

        "system_agent": """
        ⚙️ **SYSTEM AGENT**
        - Focus: technical or configuration issues (e.g., login, API setup, environment errors).
        - Capabilities:
            1. 🛠️ Diagnose platform issues
            2. 🧩 Adjust configuration or environment variables
            3. 🧾 Provide setup or troubleshooting guidance
        """,
    }

    # 🧠 Normalize the selected agents list
    if not selected_agents:
        # If no agents are provided → include all
        selected_agents = list(agent_profiles.keys())
    elif isinstance(selected_agents, str):
        selected_agents = [selected_agents]

    # 🧩 Merge all relevant agent profiles
    merged_agent_descriptions = "\n\n".join(
        agent_profiles.get(agent, agent_profiles["marketing_agent"])
        for agent in selected_agents
    )

    # 🧠 Display which agents are active
    active_agents_display = ", ".join([a.upper() for a in selected_agents])

    # 🧩 Build ONE comprehensive Task
    return Task(
        description=f"""
        You are now activating the following Siyadah AI agents together:  
        🧠 {active_agents_display}

        The user has issued this request:
        >>> {user_prompt}

        ---
        🧾 **Context Window**:
        {context_window}

        👤 **User Email**: {user_email}  
        🌍 **Language**: {user_language}  
        🌍 **Dialect**: {dialect}  
        🎭 **Tone**: {tone}  
        ⏱️ **Urgency**: {urgency}  

        ---
        ### 🔧 Agent Capabilities:
        {merged_agent_descriptions}

        ---
        🧠 **Execution Protocol**
        1. Respect tone and urgency in your reply.
        2. Always respond in {user_language} ({dialect} dialect if applicable).
        3. Use only the listed agents’ capabilities — they collaborate internally.
        4. Do not simulate or mention the orchestration layer.
        5. Produce a clear, final result (no thought process).
        6. Suggest a next step in the form of a question, based on the user input, the produced result, and the conversation context.
        7. If a misunderstanding or irrelevant response occurred in the previous turn, begin your message with a brief, polite apology (e.g., “Sorry for the confusion earlier,” or “My apologies, I misunderstood your previous question”). Then proceed directly with the correct and concise answer.

        🚨 **Critical Rules**
        - No hallucinations, no placeholders
        - Use only verified contextual data (scoped to {user_email})
        - Respect urgency: “high” = concise, “low” = detailed
        - Keep a professional and polite tone.
        - Apologize only when the system misinterprets or provides an irrelevant answer — not for normal uncertainty or lack of data.
        """,

    expected_output = f"""
        Return ONLY the final result in {user_language} ({dialect} dialect if applicable).  
        If a misunderstanding occurred previously, begin with a short apology, then provide the correct result.
        After the result, always suggest a next step in the form of a question, based on:

            the user’s input,

            the result produced,

            and the current conversation context.
            
        The result should be:
        - The actual output requested by the user (e.g., content, data, message, summary, etc.).  
        - Clean, ready to use, and formatted appropriately for the task.  

        DO NOT include:
        - Explanations or reasoning steps.  
        - Phrases like “Here is the result” or “I have completed your request.”  
        - System or agent commentary.  
        - Placeholders or unfinished content.  

        ✅ Example outputs:
        - Arabic: "تم تجهيز التقرير الشهري مع التحليل الكامل للأداء."  
        ➡️ Next step: "هل ترغب في أن أرسل هذا التقرير عبر البريد الإلكتروني لفريقك؟"  

        - English: "Customer segmentation data prepared with 120 active leads."  
        ➡️ Next step: "Would you like me to create a follow-up campaign for these leads?"  

        - Arabic (content): "مرحباً! يسعدنا إعلامك بأن عرضنا الجديد متاح الآن."  
        ➡️ Next step: "هل ترغب أن أرسل هذا العرض الآن لقاعدة عملائك؟"  

        - English (content): "Hi! Enjoy 30% off your first purchase this week."  
        ➡️ Next step: "Should I schedule this message to go out via WhatsApp or Email?"  
    """
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


@app.post("/process-prompt1/")
async def process_prompt(request: UserPromptRequest):
    """
    FastAPI endpoint that:
    1. Runs the agent and gets final result.
    2. If a file exists in ./files → include it (base64) in the response.
    3. Deletes the file after including it.
    """
    start = time.time()
    user_prompt = request.prompt
    user_email = "mohamed.akaaaq@d10.sa"
    llm_obj, manager_llm = get_llm()
    
    from utils import save_message, get_messages
    # Save user input

    save_message(redis_client, user_email, "user", user_prompt)

    # Get chat history
    from understandinglayer.simple_messages import get_response
    try:
        response = get_response(user_prompt)
        if response:
            save_message(redis_client, user_email, "system", response)
            return JSONResponse(content={
            "final_output": response,
        })
    except:
        print("there is an error occured when we are trying to get reponse fromh e defined reponses ")
    redis_context_window = get_messages(redis_client, user_email, limit=10)

    from understandinglayer.understand_prompt import PromptUnderstandingLayer

    understanding = PromptUnderstandingLayer(user_prompt, redis_context_window)
    understanding_res = understanding.understand()
    print("++++++++++++++++++++++++++++++++++++++++++++")
    print(understanding_res.to_dict())
    print("++++++++++++++++++++++++++++++++++++++++++++")
    print(understanding_res.response_type)
    from utils import respond_to_user, check_required_data
    if understanding_res.response_type == "simple":
        return JSONResponse(content={
            "final_output": respond_to_user(user_prompt, user_email),
        })

    confirmation = check_required_data(user_prompt, redis_context_window)
    if isinstance(confirmation, dict):
        if confirmation["need_details"] == "yes":
            return JSONResponse(content={
                    "final_output": confirmation['message'],
                })  

        
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print(redis_context_window)
    print(type(redis_context_window))
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    try : 
        clear_prompt= understanding_res.to_dict().get("meaning")
    except: 
        clear_prompt= user_prompt

    
    print("clear_promptclear_prompt")
    print(clear_prompt)
    print("clear_promptclear_prompt")
    try:
        tasks = planner(clear_prompt, str(redis_context_window), llm_obj)
        print(tasks)
        print(type(tasks))
    except:
        tasks = clear_prompt
    try:
        userlanguage= understanding_res.to_dict().get("meaning")
    except:
        userlanguage= "en"
    try:
        tone= understanding_res.to_dict().get("tone")
    except:
        tone = "neutral"
    try:
        urgency= understanding_res.to_dict().get("urgency")
    except:
        urgency = "normal"

    mgr = manager_agent(manager_llm, userlanguage)

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
    workers = get_workers(user_email, userlanguage, knowledge_base, str(redis_context_window))
    understand_and_execute = get_understand_and_execute_task(tasks, user_email, userlanguage, tone, urgency, str(redis_context_window))


    

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
            "user_language": userlanguage,
            "tone": tone,
            "urgency":urgency
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

@app.post("/process-prompt/")
async def process_prompt(request: UserPromptRequest):
    """
    FastAPI endpoint with Smart Manager tracking
    """
    start = time.time()
    user_prompt = request.prompt
    user_email = "mohamed.ak@d10.sa"
    llm_obj, manager_llm = get_llm()
    
    from utils import save_message, get_messages
    save_message(redis_client, user_email, "user", user_prompt)

    # Get chat history
    #from understandinglayer.simple_messages import get_response
    #try:
        #response = get_response(user_prompt)
        #if response:
            #save_message(redis_client, user_email, "system", response)
            #return JSONResponse(content={
                #"final_output": response,
            #})
    #except:
        #print("there is an error occured when we are trying to get reponse fromh e defined reponses ")
    
    redis_context_window = get_messages(redis_client, user_email, limit=10)

    from understandinglayer.understand_prompt import PromptUnderstandingLayer
    understanding = PromptUnderstandingLayer(user_prompt, redis_context_window)
    understanding_res = understanding.understand()
    print("++++++++++++++++++++++++++++++++++++++++++++")
    print(understanding_res.to_dict())
    print("++++++++++++++++++++++++++++++++++++++++++++")
    print(understanding_res.response_type)

    try:
        userlanguage = understanding_res.to_dict().get("language")
    except:
        userlanguage = "ar"
    try:
        dialect = understanding_res.to_dict().get("dialect")
    except:
        dialect = "standard"
        
    try:
        tone = understanding_res.to_dict().get("tone")
    except:
        tone = "neutral"
        
    try:
        urgency = understanding_res.to_dict().get("urgency")
    except:
        urgency = "normal"

    try:
        selected_agents = understanding_res.to_dict().get("selected_agents")
    except:
        selected_agents = []
        
    from utils import respond_to_user, check_required_data
    if understanding_res.response_type == "simple":
        return JSONResponse(content={
            "final_output": respond_to_user(user_prompt, user_email, userlanguage, dialect, tone, urgency),
        })

    confirmation = check_required_data(user_prompt, redis_context_window)
    if isinstance(confirmation, dict):
        if confirmation["need_details"] == "yes":
            return JSONResponse(content={
                "final_output": confirmation['message'],
            })  

    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print(redis_context_window)
    print(type(redis_context_window))
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    
    try: 
        clear_prompt = understanding_res.to_dict().get("meaning")
    except: 
        clear_prompt = user_prompt

    print("clear_promptclear_prompt")
    print(clear_prompt)
    print("clear_promptclear_prompt")
    
    try:
        tasks = planner(clear_prompt, str(redis_context_window), llm_obj)
        print("----------------------planner----------------------")
        print(tasks)
        print("----------------------planner----------------------")
        print(type(tasks))
    except:
        tasks = clear_prompt
        

    # 🆕 استخدام Smart Manager
    mgr = manager_agent(manager_llm, userlanguage)
    

    try:
        collection = db["knowledgebases"]
        user_doc = collection.find_one({"userId": user_email})
        knowledge_base = user_doc['extractedContent']
    except:
        knowledge_base = ""
        
    execution_time = time.time() - start
    print("-----------------------")
    print(execution_time)
    print("-----------------------")
    
    workers = get_workers(user_email, userlanguage, knowledge_base, selected_agents, str(redis_context_window))
    understand_and_execute = get_understand_and_execute_task(tasks, user_email, userlanguage, dialect, tone, urgency, selected_agents, str(redis_context_window))

    crew = Crew(
        agents=workers,
        tasks=[understand_and_execute],
        process=Process.hierarchical,
        manager_agent=mgr,
        verbose=True,
    )

    start_crew = time.time()
    try:
        final = crew.kickoff(inputs={
            "user_prompt": tasks,
            "context_window": str(redis_context_window),
            "user_email": user_email,
            "user_language": userlanguage,
            "tone": tone,
            "urgency": urgency
        })

        if hasattr(final, "raw"):
            final_output = final.raw
        elif isinstance(final, dict) and "raw" in final:
            final_output = final["raw"]
        else:
            final_output = str(final)

        # Clean the output
        final_output = clean_agent_output(final_output, userlanguage)
                    
        # Save system response
        try: 
            save_message(redis_client, user_email, "system", final_output)
        except:
            print("Sorry, i can't save the system response")
            
        crew_execution_time = time.time() - start_crew

    
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

        # 🆕 أضف الإحصائيات في الرد
        return JSONResponse(content={
            "final_output": final_output,
            "execution_time": crew_execution_time,
            "file_name": file_name,
            "file_content": file_data,
            # 🆕 معلومات إضافية
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
    

@app.post("/salla_webhook/")
async def salla_webhook_listener(request: Request):
    try:
        payload = await request.json()
        headers = dict(request.headers)
        print("=== Webhook reçu ===")
        print("Headers:", headers)
        print("Payload:", payload)
        return {"status": "ok"}
    except Exception as e:
        print("Erreur de parsing:", e)
        return {"status": "error"}
    

# ------------------------------------------------------------
# 3. Request model
# ------------------------------------------------------------
class IndexRequest(BaseModel):
    useremail: str
# ------------------------------------------------------------
# 7. Endpoint: Index user by email
# ------------------------------------------------------------
@app.post("/index_data/")
def index_data(req: IndexRequest):
    """
    Fetch user data from MongoDB (collection: knowledgebases)
    and index it into Pinecone under their namespace.
    """
    from indexing import index_user_data
    try:
        user_data = db["knowledgebases"].find_one({"userId": req.useremail})
        if not user_data or "extractedContent" not in user_data:
            raise HTTPException(status_code=404, detail="User data not found in MongoDB.")

        content = user_data["extractedContent"]
        if not content or not isinstance(content, str):
            raise HTTPException(status_code=400, detail="Invalid or empty 'extractedContent'.")

        chunk_count = index_user_data(req.useremail, content)
        return {
            "message": f"✅ Indexed {chunk_count} text chunks for {req.useremail}.",
            "namespace": req.useremail
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
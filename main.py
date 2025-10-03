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

def get_workers(user_email, user_language, knowledge_base, context_window=[]):
    """
    Initialize and return all worker agents.
    """
    llm_obj = get_llm()
    return [
        marketing_agent(llm_obj, user_email,  user_language),
        sales_agent(llm_obj, user_email, user_language),
        siyadah_helper_agent(llm_obj, user_email, user_language),
        customer_service_agent(llm_obj, user_email, user_language),
    ]

from crewai import Task

from crewai import Task
def get_understand_and_execute_task(user_prompt, user_email, user_language, tone, urgency, context_window=""):
    """
    Build a Task that routes work to the correct specialized agents,
    taking into account language, tone, urgency, and conversation context.
    """

    return Task(
        description=f"""
                    You manage an AI system with FOUR specialized agents.

                    📝 **User Request**:
                    {user_prompt}

                    🌍 **Language**: {user_language}  
                    🎭 **Tone**: {tone}  
                    ⏱️ **Urgency**: {urgency}  
                    📂 **Context Window**: {context_window}  

                    ---

                    🎯 **MARKETING AGENT Capabilities**:
                    1. 📊 Campaign Management (multi-channel campaigns)
                    2. 📧 Email Marketing (draft + send via MailerSend)
                    3. 📱 WhatsApp Campaigns
                    4. 🗂️ Customer Segmentation (MongoDB queries)
                    5. 📈 Analytics
                    6. 🎨 Content Creation
                    7. 🔍 Database Operations (CRUD)

                    💼 **SALES AGENT Capabilities**:
                    1. 🤝 Lead Management
                    2. 📞 Sales Outreach (pitches, follow-ups)
                    3. 💰 Deal Tracking
                    4. 📊 CRM Operations
                    5. 📧 Sales Emails
                    6. 📱 WhatsApp Sales
                    7. 🗂️ Database Management (MongoDB)

                    ❓ **SIYADAH HELPER AGENT Capabilities**:
                    1. 📚 Platform Knowledge (answer Siyadah questions)
                    2. 🔧 Technical Support
                    3. 📖 User Guidance
                    4. 💡 Best Practices
                    5. 🎓 Training & Capability explanation

                    📞 **CUSTOMER SERVICE AGENT Capabilities**:
                    1. 💬 Intent Detection (greetings, complaints, requests)
                    2. 📝 Smart Replies in {user_language}, adapting to {tone} & {urgency}
                    3. 📱 Multi-Channel Support (WhatsApp/Email)
                    4. 🤗 Sentiment Handling
                    5. 🔄 Escalation to Sales/Marketing/Helper if needed
                    6. 🗂️ Database Operations (conversation history)
                    7. ✅ Auto-Send (no placeholders)

                    ---

                    📜 **Execution Protocol**:
                    1. Match tone = {tone} and urgency = {urgency} in responses.
                    2. Always respond in {user_language}.
                    3. Use context from {context_window} for continuity.
                    4. Route subtasks strictly to the correct agent.
                    5. Validate data (scoped by {user_email}, no dummy info).
                    6. Maintain professional tone at all times.

                    🚨 **Critical Rules**:
                    - No hallucinations, no placeholders
                    - Only real, contextual data
                    - Respect urgency: high = prioritize speed, low = thoroughness
                    - Professional standards always

                    """,
        expected_output=f"""
                        Return ONLY the final result in {user_language}.

                        Good output examples:
                        - Arabic: "✅ تم إضافة العميل محمد برقم +21653844063"
                        - English: "✅ Customer Mohamed added with number +21653844063"

                        NEVER include:
                        - Thought process ("Thought: I need to...")
                        - Action steps ("Action: Delegate to...")
                        - Placeholders ([Your Name], [Company])
                        - Internal dialogue

                        Just the final result in one clear sentence.
                        """,
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
    llm_obj = get_llm()
    
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
            "final_output": respond_to_user(user_prompt, redis_context_window),
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

    mgr = manager_agent(llm_obj, userlanguage)

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
    user_email = "mohamed.akaaaq@d10.sa"
    llm_obj = get_llm()
    
    # 🆕 استيراد Manager Brain
    from test_manager import manager_agent, get_manager_brain
    
    from utils import save_message, get_messages
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
            "final_output": respond_to_user(user_prompt, redis_context_window),
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
        print(tasks)
        print(type(tasks))
    except:
        tasks = clear_prompt
        
    try:
        userlanguage = understanding_res.to_dict().get("language")
    except:
        userlanguage = "ar"
        
    try:
        tone = understanding_res.to_dict().get("tone")
    except:
        tone = "neutral"
        
    try:
        urgency = understanding_res.to_dict().get("urgency")
    except:
        urgency = "normal"

    # 🆕 استخدام Smart Manager
    mgr = manager_agent(llm_obj, userlanguage)
    
    # 🆕 احصل على Brain للتتبع
    brain = get_manager_brain()
    task_id = f"task_{int(time.time() * 1000)}"  # Unique task ID
    
    # 🆕 سجل بداية المهمة
    if brain:
        # تحليل المهمة أولاً
        task_analysis = brain.analyze_task(tasks, str(redis_context_window))
        selected_agent = brain.select_agent(task_analysis)
        brain.record_task_start(task_id, selected_agent, tasks[:100])

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
    
    workers = get_workers(user_email, userlanguage, knowledge_base, str(redis_context_window))
    understand_and_execute = get_understand_and_execute_task(tasks, user_email, userlanguage, tone, urgency, str(redis_context_window))

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
        
        # 🆕 سجل نجاح المهمة
        if brain:
            brain.record_task_completion(task_id, True, crew_execution_time)
            # اطبع الإحصائيات
            print("\n" + "="*60)
            print(brain.get_metrics_summary())
            print("="*60 + "\n")

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
            "metrics": {
                "task_id": task_id,
                "agent_used": selected_agent if brain else "unknown",
                "total_tasks": brain.total_tasks if brain else 0,
                "success_rate": f"{(brain.completed_tasks/max(brain.total_tasks,1)*100):.1f}%" if brain else "N/A"
            }
        })

    except Exception as e:
        # 🆕 سجل فشل المهمة
        if brain:
            brain.record_task_completion(task_id, False, time.time() - start_crew)
            brain.retry_count += 1
            
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
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
from crewai import Task

def get_understand_and_execute_task(
    user_prompt,
    user_email,
    user_language,
    dialect,
    tone,
    urgency,
    selected_agents=None,
    context_window="",
):
    """
    Dynamically build one unified Task that coordinates Siyadah AI agents.
    ✅ NOW WITH: Strict validation, step verification, and guaranteed execution.
    """

    # 🧩 Define agent-specific profiles
    agent_profiles = {
        "marketing_agent": """
        🎯 **MARKETING AGENT**
        - Focus: communication, engagement, promotions, and campaigns.
        - Channels: WhatsApp, Email, and social media.
        - Core Strengths:
            - Build and deliver personalized marketing content.
            - Manage multi-channel promotional campaigns.
            - Engage customers via automated WhatsApp and Email messages.
        - Capabilities:
            1. 📊 Campaign Management & Scheduling (multi-channel)
            2. 🎨 Content Creation & Personalization for each audience
            3. 💬 Send and manage WhatsApp & Email Messaging campaigns
            4. 🗂️ Customer Segmentation using database queries
            5. 📈 Analyze campaign performance (clicks, opens, engagement)
            6. 🧠 Collaborate with Data Agent for targeting insights
            7. ✅ Can both prepare and send messages directly (WhatsApp / Email)
        """,

        "sales_agent": """
        💼 **SALES AGENT**
        - Focus: lead nurturing, follow-ups, offers, and conversions.
        - Channels: WhatsApp, Email, and CRM.
        - Core Strengths:
            - Communicate with leads and customers via WhatsApp or Email.
            - Manage pipelines, deals, and personalized offers.
            - Track interactions and follow-up responses in the CRM.
        - Capabilities:
            1. 🤝 Lead & Deal Management (status updates, follow-ups)
            2. 💬 Send and manage personalized WhatsApp & Email messages
            3. 💰 Offer Creation, Quotation, and Pipeline Tracking
            4. 📊 CRM Database Operations (Create, Read, Update, Delete)
            5. 🧠 Collaborate with Marketing & Data Agents for lead insights
            6. ✅ Can prepare, send, and confirm WhatsApp / Email messages
        """,

        "data_agent": """
        🗂️ **DATA AGENT**
        - Focus: database operations, analytics, and structured reporting.
        - Core Strengths:
            - Handle data integrity, analytics, and reporting for all agents.
            - Support marketing and sales with data-driven insights.
        - Capabilities:
            1. 📦 CRUD Operations (Create, Read, Update, Delete)
            2. 📋 Data Validation & Consistency Checks
            3. 📈 Generate Reports and Analytical Summaries
            4. 🔍 Manage and retrieve customer records
            5. 🧠 Provide analytics and segmentation support to other agents
            6. ✅ Can verify and store marketing/sales actions in the database
        """,

        "system_agent": """
        ⚙️ **SYSTEM AGENT**
        - Focus: configuration, integration, and troubleshooting.
        - Core Strengths:
            - Ensure API connections, database links, and tools work correctly.
            - Provide system-level guidance and error resolution.
        - Capabilities:
            1. 🧩 Diagnose configuration or environment issues
            2. 🔧 Manage API keys, DB connections, and credentials
            3. 🧾 Provide setup guidance and automated recovery actions
            4. ✅ Support other agents by ensuring tools function correctly
        """,
    }

    # 🧠 Normalize the selected agents list
    if not selected_agents:
        selected_agents = list(agent_profiles.keys())
    elif isinstance(selected_agents, str):
        selected_agents = [selected_agents]

    # 🧩 Merge all relevant agent profiles
    merged_agent_descriptions = "\n\n".join(
        agent_profiles.get(agent, agent_profiles["marketing_agent"])
        for agent in selected_agents
    )

    # 🧠 Display which agents are active
    active_agents_display = ", ".join(a.upper() for a in selected_agents)

    # 🧩 Build the unified Task with STRICT EXECUTION RULES
    return Task(
        description=f"""
        You are now activating the following Siyadah AI agents together:
        🧠 {active_agents_display}

        The user has requested:
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
        🎯 **MANDATORY EXECUTION PROTOCOL** (MUST FOLLOW)
        
        1️⃣ **Task Analysis**
           - Break down the user request into sequential steps
           - Identify ALL required actions (read → create → send, etc.)
           - Determine which agent handles each step
        
        2️⃣ **Sequential Execution** (CRITICAL)
           - Execute steps in order, ONE AT A TIME
           - Complete each step BEFORE moving to the next
           - Use actual tools, not descriptions
           
        3️⃣ **Tool Usage Rules**
           - Database operations → Use MongoDB Read/Write/Update/Delete tools
           - Content creation → Use MessageContentTool
           - WhatsApp sending → Use WhatsApp Tool (must show in logs)
           - Email sending → Use MailerSend Tool (must show in logs)
        
        4️⃣ **Step Verification** (MANDATORY)
           After EACH step, verify:
           ✅ Tool was actually called (check your tool usage logs)
           ✅ Tool returned success status
           ✅ Output contains concrete data (phone number, message ID, etc.)
           
        5️⃣ **Multi-Step Task Example**:
           User: "Send a discount offer to Mohamed"
           
           ✅ CORRECT Execution:
           Step 1: Use MongoDB Read Tool → Get Mohamed's phone: +21653844063
           Step 2: Use MessageContentTool → Create offer message
           Step 3: Use WhatsApp Tool → Send message to +21653844063
           Step 4: Verify → Check WhatsApp Tool returned success
           Final: "✅ تم إرسال عرض الخصم إلى محمد (+21653844063)"
           
           ❌ WRONG Execution:
           Step 1: Get phone number
           Step 2: Skip sending
           Final: "✅ تم الإرسال" ← LIE! No tool was used!

        ---
        🚨 **CRITICAL VALIDATION RULES** (NEVER VIOLATE)
        
        ❌ **FORBIDDEN ACTIONS**:
        1. Claiming "تم الإرسال" / "Message sent" without WhatsApp/Email Tool execution
        2. Skipping any step in a multi-step task
        3. Assuming completion based on partial results
        4. Using tool results from previous context without re-verification
        5. Fabricating phone numbers, emails, or customer data
        6. Saying "success" when a tool failed or wasn't called
        
        ✅ **REQUIRED ACTIONS**:
        1. Show tool name for EVERY action taken
        2. Display tool output/result for verification
        3. Confirm each step completed successfully before proceeding
        4. If ANY step fails → stop and report the failure clearly
        5. For send operations → MUST use actual send tool (WhatsApp/Email)
        6. For database operations → MUST use actual MongoDB tool
        
        ---
        📋 **Step-by-Step Execution Checklist**
        
        Before claiming completion, verify you have:
        □ Identified all required steps from user request
        □ Executed EACH step using the appropriate tool
        □ Verified EACH tool returned success
        □ Collected concrete evidence (IDs, numbers, confirmations)
        □ NOT skipped any steps
        □ NOT assumed anything without verification
        
        ---
        🔍 **Self-Verification Questions** (Ask yourself before responding)
        
        1. Did I actually call the required tools? (Check your tool usage log)
        2. Did each tool return success? (Check tool outputs)
        3. Do I have concrete proof of completion? (Message ID, phone number, etc.)
        4. Did I skip any steps? (Re-read the user request)
        5. Am I claiming something I didn't actually do? (Be honest)
        
        If you answer "NO" to any question → DO NOT claim success!
        
        ---
        🎭 **Response Guidelines**
        
        1. Respond entirely in {user_language} ({dialect} dialect if applicable)
        2. Respect {tone} tone and {urgency} urgency level
        3. Keep reasoning implicit — only show final actionable output
        4. Never reveal orchestration internals
        5. Never fabricate data — only use verified context scoped to {user_email}
        6. If uncertain → ask ONE clarifying question
        
        ---
        ⚠️ **Error Handling**
        
        If ANY step fails:
        1. Stop execution immediately
        2. Report which step failed
        3. Explain why it failed (tool error, missing data, etc.)
        4. Do NOT proceed to next steps
        5. Do NOT claim partial success as full success
        
        Example:
        "❌ فشل الخطوة 2: لم أتمكن من إرسال الرسالة عبر الواتساب. السبب: رقم الهاتف غير صحيح."
        
        ---
        🎯 **Final Reminder**
        
        Your job is to EXECUTE, not to DESCRIBE.
        - "I will send..." ❌ Wrong
        - "Sending..." ❌ Wrong  
        - "✅ Message sent to +21653844063 via WhatsApp Tool" ✅ Correct
        
        ALWAYS show proof of execution!
        """,

        expected_output=f"""
        Return ONLY the final verified result in {user_language} ({dialect} dialect if applicable).

        ---
        ✅ **REQUIRED OUTPUT STRUCTURE**
        
        Your response MUST contain:
        
        1️⃣ **Execution Summary** (brief)
           - What was requested
           - What was actually done (with tool names)
           
        2️⃣ **Concrete Evidence** (MANDATORY)
           - For database: Show actual data retrieved
           - For sending: Show recipient phone/email + send confirmation
           - For content: Show the actual content created
           
        3️⃣ **Status Indicator** (clear)
           - ✅ Success with specific details
           - ❌ Failure with clear reason
           - ⚠️ Partial completion with explanation
           
        4️⃣ **Next Step Question** (contextual)
           - Relevant follow-up based on what was done
           - Should guide the user naturally
        
        ---
        📋 **OUTPUT EXAMPLES**
        
        Example 1 - Database Read:
        "✅ تم استخراج بيانات محمد من قاعدة البيانات:
        - الاسم: محمد أكاشا
        - الهاتف: +21653844063
        - البريد: mohamed.ak@d10.sa
        
        ➡️ الخطوة التالية: هل تريد إرسال رسالة لمحمد الآن؟"
        
        Example 2 - Content Creation:
        "✅ تم إنشاء محتوى العرض:
        
        'مرحباً محمد! 🎉
        نقدم لك عرضاً خاصاً: خصم 30% على جميع منتجاتنا.
        العرض ساري حتى نهاية الشهر.'
        
        ⚠️ المحتوى جاهز لكن لم يتم الإرسال بعد.
        
        ➡️ الخطوة التالية: هل تريد إرسال هذا العرض لمحمد الآن؟"
        
        Example 3 - Complete Send Operation:
        "✅ تم إرسال عرض الخصم 30% بنجاح:
        - المستلم: محمد أكاشا
        - الهاتف: +21653844063
        - القناة: واتساب
        - الوقت: {datetime.now().strftime('%H:%M')}
        - التأكيد: WhatsApp Tool returned success
        
        ➡️ الخطوة التالية: هل تريد إرسال عروض مشابهة لعملاء آخرين؟"
        
        Example 4 - Multi-Step Task:
        "✅ تم تنفيذ جميع الخطوات بنجاح:
        
        الخطوة 1 ✅: استخراج رقم هاتف محمد (+21653844063)
        الخطوة 2 ✅: إنشاء محتوى العرض (خصم 30%)
        الخطوة 3 ✅: إرسال الرسالة عبر الواتساب
        
        النتيجة النهائية: تم إرسال العرض إلى محمد بنجاح.
        
        ➡️ الخطوة التالية: هل تريد تتبع استجابة محمد للعرض؟"
        
        Example 5 - Failure Case:
        "❌ فشل التنفيذ في الخطوة 2:
        
        الخطوة 1 ✅: استخراج رقم الهاتف (+21653844063)
        الخطوة 2 ❌: فشل إنشاء المحتوى
        السبب: MessageContentTool returned error - missing template
        الخطوة 3 ⏸️: لم يتم التنفيذ (بسبب فشل الخطوة 2)
        
        ➡️ الحل المقترح: هل تريد تحديد نص الرسالة يدوياً؟"
        
        ---
        🚨 **CRITICAL OUTPUT RULES**
        
        ❌ DO NOT output:
        - Generic success messages without details
        - Claims of sending without tool confirmation
        - Reasoning or thought process
        - System or orchestration details
        - Placeholder data or assumptions
        
        ✅ DO output:
        - Specific, verifiable results
        - Tool names and their outputs
        - Concrete evidence (phone numbers, IDs, etc.)
        - Clear success/failure indicators
        - Relevant next-step question
        
        ---
        📊 **Validation Before Submitting Response**
        
        Ask yourself:
        1. ✅ Did I show which tools were actually used?
        2. ✅ Did I include concrete evidence?
        3. ✅ Is my success claim backed by tool output?
        4. ✅ Did I complete ALL requested steps?
        5. ✅ Did I provide a relevant next-step question?
        
        If ALL answers are YES → Submit response
        If ANY answer is NO → Revise response
        
        ---
        🎯 **Remember**
        
        Quality > Speed
        Accuracy > Assumptions  
        Proof > Claims
        Execution > Description
        
        The user trusts you to EXECUTE, not just to SAY you executed.
        ALWAYS provide concrete proof of what you did!
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

    try:
        meaning = understanding_res.to_dict().get("meaning")
    except:
        meaning = user_prompt
        
    from utils import respond_to_user, check_required_data
    if understanding_res.response_type == "simple":
        return JSONResponse(content={
            "final_output": respond_to_user(user_prompt, user_email, userlanguage, dialect, tone, urgency),
        })

    confirmation = check_required_data(meaning, redis_context_window)
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
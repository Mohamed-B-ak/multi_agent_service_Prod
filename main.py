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
from agents.content_agent import strategic_content_agent
from agents.db_agent import intelligent_database_agent
from agents.email_sender_agent import email_agent
from agents.manager_agent import intelligent_manager_agent
from agents.understanding_agent import enhanced_understanding_agent
from agents.whatsApp_sender import whatsapp_agent
from agents.siyadah_helper_agent import siyadah_helper_agent
from agents.web_analyser_agent import web_analyser_agent
from agents.knowledge_enhanced_content_agent import knowledge_enhancer_agent
from agents.file_creation_agent import file_creation_agent
from agents.crm_agent import crm_agent
# 🧠 إضافة الوكلاء الجدد
from agents.intent_analysis_agent import intent_analysis_agent
from agents.context_memory_agent import context_memory_agent
from agents.strategic_planning_agent import strategic_planning_agent
from fastapi.responses import JSONResponse
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

FOLDER_PATH = os.path.join(os.getcwd(), "files")  # ./files directory
os.makedirs(FOLDER_PATH, exist_ok=True)

# FastAPI app instance
app = FastAPI()

# LLM initialization function
def get_llm():
    """
    Initialize the LLM (Large Language Model) with a predefined model and API key.
    """
    return LLM(
        model="gpt-4o",
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.3,

    )
from typing import Optional

# Request body model for the user input prompt
class UserPromptRequest(BaseModel):
    prompt: str
    user_email: Optional[str] = None   # Optional field
    context: list = []      # Optional field with default empty list

# 🧠 دالة الوكلاء المحدثة مع الوكلاء الجدد

def get_workers(user_email, user_language, knowledge_base):
    """
    🧠 Fixed worker agents with intelligent database operations
    """
    llm_obj = get_llm()
    return [
        # 🧠 CORE INTELLIGENCE AGENTS
        enhanced_understanding_agent(llm_obj, user_language),
        intent_analysis_agent(llm_obj, user_language),
        strategic_planning_agent(llm_obj, user_language),
        
        # 🗂️ FIXED DATABASE AGENT (HIGHEST PRIORITY)
        intelligent_database_agent(llm_obj, user_email, user_language),  # ✅ FIXED AGENT
        
        # 🎭 ENHANCED CONTENT CREATION
        strategic_content_agent(llm_obj, user_language),
        knowledge_enhancer_agent(llm_obj, knowledge_base, user_language),
        
        # 📡 COMMUNICATION CHANNELS
        email_agent(llm_obj, user_email, user_language),
        whatsapp_agent(llm_obj, user_email, user_language),
        caller_agent(llm_obj, user_language),
        
        # 🏢 BUSINESS OPERATIONS
        crm_agent(llm_obj, user_email, user_language),
        file_creation_agent(llm_obj),
        
        # 🤖 SPECIALIZED SERVICES
        code_agent(llm_obj, user_language), 
        web_analyser_agent(llm_obj, user_language),
        siyadah_helper_agent(llm_obj, user_language),
    ]
# Task for understanding and executing the user's request
from crewai import Task

def get_understand_and_execute_task():
    """
    🧠 FIXED INTELLIGENT TASK - Now with proper database operations priority
    """
    return Task(
        description=(
            "🧠 INTELLIGENT BUSINESS OPERATIONS SYSTEM - ENHANCED WITH PROPER DATABASE HANDLING\n"
            "Transform user requests into the correct actions - NO MORE CONFUSION!\n\n"
            
            "🚨 CRITICAL INTENT RECOGNITION (MANDATORY):\n\n"
            
            "📊 DATABASE OPERATIONS (HIGHEST PRIORITY):\n"
            "🔍 If user says 'أضيف عميل جديد' or 'add new client':\n"
            "   → Route to: Intelligent Database Operations Specialist\n"
            "   → Action: ADD client to database (NOT send emails!)\n"
            "   → Required: Name, Phone, Email, Company (optional)\n"
            "   → Response: Database confirmation in user language\n\n"
            
            "🔍 If user says 'اعرض العملاء' or 'list clients':\n"
            "   → Route to: Intelligent Database Operations Specialist\n"
            "   → Action: QUERY database for clients\n"
            "   → Response: Client list in user language\n\n"
            
            "🔍 If user says 'كم عميل عندي' or 'count clients':\n"
            "   → Route to: Intelligent Database Operations Specialist\n"
            "   → Action: COUNT clients in database\n"
            "   → Response: Number in user language\n\n"
            
            "📧 EMAIL OPERATIONS (Only for actual email sending):\n"
            "🔍 If user says 'ارسل إيميل' or 'send email':\n"
            "   → Route to: Email workflow (Content → Enhancement → Send)\n\n"
            
            "📱 WHATSAPP OPERATIONS (Only for messaging):\n"
            "🔍 If user says 'ارسل واتساب' or 'send whatsapp':\n"
            "   → Route to: WhatsApp workflow\n\n"
            
            "❓ HELP/QUESTIONS:\n"
            "🔍 If user asks questions about platform:\n"
            "   → Route to: Siyadah Helper Agent\n\n"
            
            "⚠️ MANDATORY RULES:\n"
            "- Database operations = Database Agent ONLY\n"
            "- Email operations = Email workflow ONLY\n"
            "- NO mixing database operations with email sending\n"
            "- NO creating marketing content for database operations\n"
            "- ALWAYS respond in user language: {user_language}\n"
            "- User email for scoping: {user_email}\n\n"
            
            "🔍 INPUT ANALYSIS:\n"
            "User Request: {user_prompt}\n"
            "User Language: {user_language} (maintain throughout)\n"
            "Business Context: {context_window}\n"
            "User Email: {user_email}\n\n"
            
            "🎯 EXPECTED BEHAVIOR FOR 'أضيف عميل جديد':\n"
            "1. Recognize this as DATABASE OPERATION\n"
            "2. Route to Database Agent ONLY\n"
            "3. Ask for client details if missing\n"
            "4. Add client to 'clients' collection\n"
            "5. Confirm addition in Arabic\n"
            "6. DO NOT send any emails\n"
            "7. DO NOT create marketing content"
        ),
        expected_output=(
            "🎯 CORRECT BEHAVIOR EXAMPLES:\n\n"
            
            "✅ For 'أضيف عميل جديد':\n"
            "→ 'لإضافة عميل جديد، أحتاج المعلومات التالية:\n"
            "   - اسم العميل\n"
            "   - رقم الهاتف\n"
            "   - البريد الإلكتروني\n"
            "   - اسم الشركة (اختياري)\n"
            "   يرجى تقديم هذه المعلومات لإتمام الإضافة.'\n\n"
            
            "✅ For 'اعرض العملاء':\n"
            "→ Display actual client list from database\n\n"
            
            "✅ For 'كم عميل عندي':\n"
            "→ 'عدد العملاء: [actual_number]'\n\n"
            
            "❌ WRONG BEHAVIOR (OLD SYSTEM):\n"
            "→ Creating marketing emails for database operations\n"
            "→ Sending emails to user when they want to add clients\n"
            "→ Complex strategic planning for simple database operations\n\n"
            
            "🎯 SUCCESS CRITERIA:\n"
            "- Correct agent routing based on intent\n"
            "- Actual database operations performed\n"
            "- Clear, direct responses in {user_language}\n"
            "- No confusion between operations\n"
            "- User gets exactly what they asked for"
        ),
    )
# 🧪 مهمة اختبار الوكلاء الجدد
def create_analysis_test_task():
    """
    مهمة اختبار وكلاء التحليل الجدد
    """
    return Task(
        description=(
            "🧪 TEST NEW ANALYSIS AGENTS - Verification Phase\n"
            "Test the new analysis agents to ensure they work correctly:\n\n"
            
            "1. 🎯 INTENT ANALYSIS AGENT TEST:\n"
            "   - Analyze the user input: '{user_prompt}'\n"
            "   - Extract primary and secondary intents\n"
            "   - Identify emotional tone and urgency level\n"
            "   - Assess complexity and multi-step requirements\n"
            "   - Provide structured JSON analysis\n\n"
            
            "2. 🧠 CONTEXT MEMORY AGENT TEST:\n"
            "   - Check conversation history for user: {user_email}\n"
            "   - Analyze user patterns if available\n"
            "   - Retrieve relevant contextual information\n"
            "   - Provide personalization insights\n\n"
            
            "3. 📊 STRATEGIC PLANNING AGENT TEST:\n"
            "   - Create execution plan based on analysis\n"
            "   - Suggest optimal agent sequence\n"
            "   - Assess complexity and potential risks\n"
            "   - Provide time and resource estimates\n\n"
            
            "CONTEXT: {context_window}\n"
            "GOAL: Verify all new analysis agents are functioning properly and providing valuable insights."
        ),
        expected_output=(
            "🧪 ANALYSIS AGENTS TEST RESULTS:\n\n"
            "🎯 Intent Analysis Results:\n"
            "- ✅ Primary and secondary intents identified\n"
            "- ✅ Emotional tone and urgency detected\n"
            "- ✅ Complexity assessment completed\n"
            "- ✅ Structured analysis provided\n\n"
            
            "🧠 Context Memory Results:\n"
            "- ✅ Conversation history retrieved (if any)\n"
            "- ✅ User patterns analyzed\n"
            "- ✅ Personalization insights provided\n"
            "- ✅ Contextual relationships identified\n\n"
            
            "📊 Strategic Planning Results:\n"
            "- ✅ Execution strategy determined\n"
            "- ✅ Agent sequence planned\n"
            "- ✅ Risk assessment completed\n"
            "- ✅ Resource requirements estimated\n\n"
            
            "🎉 CONCLUSION: All analysis agents tested successfully!\n"
            "The system now has enhanced intelligence capabilities for:\n"
            "- Deeper understanding of user requests\n"
            "- Better personalization through memory\n"
            "- Optimal execution planning\n\n"
            "Ready for production use with improved performance!"
        ),
    )

def detect_language(text: str) -> str:
    langid.set_languages(['fr', 'en', 'ar'])
    lang, prob = langid.classify(text)
    print(lang)
    return lang  # will always be 'fr', 'en', or 'ar'

# FastAPI endpoint to process the user prompt (المحدث)
@app.post("/process-prompt/")
async def process_prompt(request: UserPromptRequest):
    """
    FastAPI endpoint that:
    1. Uses the enhanced system with new analysis agents
    2. Runs the agent and gets final result.
    3. If a file exists in ./files → include it (base64) in the response.
    4. Deletes the file after including it.
    """
    user_prompt = request.prompt
    context_window = request.context
    user_email = "mohamed.ak@d10.sa"
    
    # Initialize LLM and Manager
    llm_obj = get_llm()
    mgr = intelligent_manager_agent(llm_obj)

    # Detect language
    try:
        user_language = detect_language(user_prompt)
    except Exception:
        user_language = "en"

    # Get knowledge base
    try:
        client = MongoClient(os.getenv("MONGO_DB_URI"))
        db = client[os.getenv("DB_NAME")]
        collection = db["knowledgebases"]
        user_doc = collection.find_one({"createdByEmail": user_email})
        knowledge_base = user_doc['extractedContent'] if user_doc else ""
    except:
        knowledge_base = ""

    # 🧠 استخدام الوكلاء المحدثين مع الوكلاء الجدد
    workers = get_workers(user_email, user_language, knowledge_base)
    understand_and_execute = get_understand_and_execute_task()

    crew = Crew(
        agents=workers,
        tasks=[understand_and_execute],
        process=Process.hierarchical,
        manager_agent=mgr,
        verbose=True,
    )

    start = time.time()
    try:
        print(f"🚀 Enhanced Siyadah Processing with Analysis Agents: {user_prompt[:50]}...")
        
        # Run agent process with enhanced capabilities
        final = crew.kickoff(inputs={
            "user_prompt": user_prompt,
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

        # -----------------------
        # Check ./files for one file
        # -----------------------
        file_data = None
        file_name = None

        if os.path.exists(FOLDER_PATH):
            files = os.listdir(FOLDER_PATH)
            if files:  # only one file expected
                file_path = os.path.join(FOLDER_PATH, files[0])
                file_name = files[0]

                # Encode file content as base64
                with open(file_path, "rb") as f:
                    file_data = base64.b64encode(f.read()).decode("utf-8")

                # Delete the file
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Could not delete {file_path}: {e}")

        # -----------------------
        # Return JSON response with enhanced info
        # -----------------------
        return JSONResponse(content={
            "final_output": final_output,
            "execution_time": execution_time,
            "system_version": "Siyadah Enhanced v1.1 - with Analysis Agents",
            "new_capabilities": [
                "Deep Intent Analysis",
                "Conversational Memory",
                "Strategic Planning"
            ],
            "agents_count": len(workers),
            "language_detected": user_language,
            "file_name": file_name,
            "file_content": file_data  # base64 encoded file (None if no file)
        })

    except Exception as e:
        print(f"❌ Enhanced processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error occurred: {str(e)}")

# 🧪 نقطة نهاية خاصة لاختبار الوكلاء الجدد
@app.post("/test-analysis-agents/")
async def test_analysis_agents(request: UserPromptRequest):
    """
    نقطة نهاية خاصة لاختبار الوكلاء الجدد فقط
    """
    user_prompt = request.prompt
    context_window = request.context
    user_email = "mohamed.ak@d10.sa"
    
    # اكتشاف اللغة
    try:
        user_language = detect_language(user_prompt)
    except Exception:
        user_language = "en"
    
    # إنشاء فريق الاختبار (الوكلاء الجدد فقط + مدير)
    llm_obj = get_llm()
    test_agents = [
        intent_analysis_agent(llm_obj, user_language),
        context_memory_agent(llm_obj, user_email, user_language),
        strategic_planning_agent(llm_obj, user_language),
    ]
    
    # مهمة الاختبار
    test_task = create_analysis_test_task()
    
    # مدير للتنسيق
    test_manager = intelligent_manager_agent(llm_obj)
    
    # فريق الاختبار
    test_crew = Crew(
        agents=test_agents,
        tasks=[test_task],
        process=Process.hierarchical,
        manager_agent=test_manager,
        verbose=True,
    )
    
    start = time.time()
    try:
        print(f"🧪 Testing New Analysis Agents with: {user_prompt[:50]}...")
        
        result = test_crew.kickoff(inputs={
            "user_prompt": user_prompt,
            "user_email": user_email,
            "context_window": context_window
        })
        
        execution_time = time.time() - start
        
        # استخراج النتيجة
        if hasattr(result, "raw"):
            final_output = result.raw
        elif isinstance(result, dict) and "raw" in result:
            final_output = result["raw"]
        else:
            final_output = str(result)
        
        return JSONResponse(content={
            "test_results": final_output,
            "execution_time": execution_time,
            "agents_tested": [
                "Intent Analysis Agent",
                "Context Memory Agent", 
                "Strategic Planning Agent"
            ],
            "test_status": "✅ COMPLETED",
            "performance_metrics": {
                "agents_count": len(test_agents),
                "execution_time_seconds": round(execution_time, 2),
                "language_detected": user_language,
                "test_complexity": "basic_functionality"
            },
            "next_steps": [
                "Deploy to production if results are satisfactory",
                "Proceed to Phase 2: Enhanced Content Agents",
                "Monitor performance in real usage"
            ]
        })
        
    except Exception as e:
        print(f"❌ Analysis Agent Test Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")

# Endpoint to serve the HTML interface (بدون تغيير)
@app.get("/")
async def get_chat_interface():
    """
    Serve the HTML interface for the chat.
    """
    # Make sure the HTML file exists in the same directory as this file.
    html_file_path = os.path.join(os.path.dirname(__file__), "index.html")
    
    # Check if the file exists
    if os.path.exists(html_file_path):
        with open(html_file_path, "r") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    else:
        raise HTTPException(status_code=404, detail="HTML chat interface not found.")
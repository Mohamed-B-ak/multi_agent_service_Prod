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
    إضافة الوكلاء الجدد للفريق الموجود
    """
    llm_obj = get_llm()
    return [
        # 🧠 وكلاء التحليل الجدد - الإضافة الجديدة
        intent_analysis_agent(llm_obj, user_language),
        strategic_planning_agent(llm_obj, user_language),
        
        # 🔄 الوكلاء الموجودين (بدون تغيير)
        understanding_agent(llm_obj),
        content_agent(llm_obj, user_language),
        email_agent(llm_obj, user_email, user_language),
        whatsapp_agent(llm_obj, user_email, user_language),
        caller_agent(llm_obj, user_language),
        code_agent(llm_obj, user_language), 
        db_agent(llm_obj, user_email, user_language),
        siyadah_helper_agent(llm_obj, user_language),
        knowledge_enhancer_agent(llm_obj, knowledge_base, user_language),
        file_creation_agent(llm_obj),
        crm_agent(llm_obj, user_email, user_language),
    ]

# Task for understanding and executing the user's request
from crewai import Task

def get_understand_and_execute_task():
    """
    تعريف وإرجاع المهمة لفهم وتنفيذ موجهات المستخدم، مع استخدام السياق داخليًا فقط إن كان ذا صلة.
    النظام يدعم قنوات متعددة: البريد الإلكتروني، الواتساب، المكالمات،
    قواعد البيانات، تحليل المواقع، إنشاء الملفات، CRM Agent (للاستعلام فقط)،
    ووكيل المعرفة Siyadah.
    """

    return Task(
        description=(
            "🧠 ENHANCED SYSTEM WITH ADVANCED ANALYSIS - Now with intelligent analysis agents!\n"
            "You now have access to powerful analysis agents that provide deep insights:\n\n"
            
            "🎯 NEW ANALYSIS CAPABILITIES:\n"
            "1. 🧠 INTENT ANALYSIS AGENT: Deep understanding of user requests, emotions, and hidden meanings\n"
            "2. 💭 CONTEXT MEMORY AGENT: Remembers past conversations and user patterns\n"
            "3. 📊 STRATEGIC PLANNING AGENT: Creates optimal execution plans\n\n"
            
            "💡 HOW TO USE THE NEW AGENTS:\n"
            "- For complex requests: First consult Intent Analysis Agent for deep understanding\n"
            "- For personalized responses: Use Context Memory Agent to recall user preferences\n"
            "- For optimal execution: Let Strategic Planning Agent create the best approach\n\n"
            
            "أنت تدير نظام ذكاء اصطناعي للتواصل والبرمجة قادر على:\n"
            "1. 📧 **محتوى البريد الإلكتروني**: صياغة بريد إلكتروني احترافي باستخدام أخصائي المحتوى + وكيل تعزيز المحتوى.\n"
            "2. 📤 **إرسال البريد الإلكتروني**: يتم فقط بطلب صريح وبعد تمرير المحتوى لوكيل تعزيز المحتوى.\n"
            "3. 📱 **محتوى واتساب**: صياغة رسائل باستخدام أخصائي المحتوى + وكيل تعزيز المحتوى.\n"
            "4. 📲 **إرسال واتساب**: يتم فقط بطلب صريح مع تمرير المحتوى عبر وكيل تعزيز المحتوى.\n"
            "5. ☎️ **نصوص المكالمات**: سكربت مبدئي من أخصائي المحتوى + تحسين عبر وكيل تعزيز المحتوى.\n"
            "6. ☎️ **إجراء مكالمة**: بعد التأكيد فقط.\n"
            "7. 🗂️ **عمليات قاعدة البيانات (MongoDB)**: تنفيذ CRUD (إضافة، تعديل، حذف، استعلام) مقيدة ببريد المستخدم {user_email}.\n"
            "8. 📄 **إنشاء ملفات PDF أو Word أو Excel**: باستخدام File Creator Agent وحفظ الناتج في مجلد 'files/'.\n"
            "9. 🏢 **إدارة CRM (HubSpot, Salesforce, Zoho, ...)**: يقتصر دورها فقط على *استخراج أو عرض بيانات العملاء* عند تصريح المستخدم.\n"
            "10. 🤖 **أسئلة واستفسارات Siyadah**: تمريرها إلى وكيل المساعد الذكي Siyadah Intelligent Agent.\n\n"

            "🧠 سياسة استخدام السياق (داخليًا فقط):\n"
            "- يمكن استخدام {context_window} لفهم الموجه واستكمال النواقص عند الحاجة، دون عرض تلخيص أو إحالات للسياق.\n"
            "- طلب المستخدم الصريح له الأولوية إذا تعارض مع السياق.\n\n"

            "📝 وضع الإيجاز الصارم (Strict Concision):\n"
            "- أجب على قدر السؤال فقط دون إضافات.\n"
            "- نعم/لا تُجاب باختصار.\n\n"

            "طلب المستخدم: {user_prompt}\n\n"

            "📌 التوجيه الذكي المطور - الإجباري:\n"
            "🎯 لجميع الطلبات: استشر Intent Analysis Agent أولاً (إجباري)\n"
            "📊 لجميع الطلبات: اطلب من Strategic Planning Agent وضع خطة تنفيذ\n"
            "📧 نية = 'صياغة بريد إلكتروني' → أخصائي المحتوى + وكيل تعزيز المحتوى\n"
            "📧 نية = 'إرسال بريد إلكتروني' → أخصائي المحتوى + وكيل تعزيز المحتوى + أخصائي البريد الإلكتروني\n"
            "📱 نية = 'صياغة واتساب' → أخصائي المحتوى + وكيل تعزيز المحتوى\n"
            "📱 نية = 'إرسال واتساب' → أخصائي المحتوى + وكيل تعزيز المحتوى + أخصائي واتساب\n"
            "☎️ نية = 'صياغة مكالمة' → أخصائي المحتوى + وكيل تعزيز المحتوى\n"
            "☎️ نية = 'إجراء مكالمة' → أخصائي المحتوى + وكيل تعزيز المحتوى + أخصائي المكالمات\n"
            "🗂️ نية = 'عمليات قاعدة بيانات' (إضافة/تعديل/حذف/استعلام) → أخصائي قاعدة البيانات\n"
            "📝 نية = 'إنشاء ملف PDF أو Word أو Excel' → File Creator Agent\n"
            "🏢 نية = 'CRM' → استدعاء CRM Agent فقط لاستخراج/عرض بيانات العملاء عند تصريح المستخدم.\n"
            "❓ نية = 'استفسار' أو 'مساعدة' → Siyadah Intelligent Agent\n"
            "🔄 نوايا متعددة → التنسيق بين الوكلاء\n"
            "❓ نية غير واضحة أو بيانات ناقصة → استيضاح ذكي بسؤال مباشر قبل التنفيذ.\n\n"

            "📜 بروتوكول التنفيذ المحدث - الإجباري:\n"
            "1. الكشف عن لغة المستخدم.\n"
            "2. 🧠 استشارة Intent Analysis Agent للفهم العميق (إجباري لجميع الطلبات)\n"
            "4. 📊 استشارة Strategic Planning Agent للتخطيط (إجباري)\n"
            "5. الرد بنفس لغة المستخدم.\n"
            "6. في *الصياغة*: يولّد المحتوى ثم يُحسّن.\n"
            "7. في *الإرسال*: صياغة + تعزيز ثم تمرير لوكيل القناة.\n"
            "8. في *قاعدة البيانات*: جميع عمليات الإضافة والتعديل والحذف تُنفذ على DB الداخلية فقط.\n"
            "9. في *الملفات*: إنشاء الملف عبر File Creator Agent وحفظه في مجلد 'files/'.\n"
            "10. في *إدارة CRM*: يسمح فقط بالاستعلام/الاستخراج عند تصريح المستخدم.\n"
            "11. في استفسارات Siyadah: تمريرها إلى الوكيل المعرفي.\n"
            "12. الأسئلة المباشرة: إجابة مقتضبة.\n"
            "13. في حالة النية الغامضة أو نقص البيانات: طرح سؤال استيضاح قبل أي تنفيذ.\n"
            "14. التأكيد فقط في حالة الأوامر التنفيذية.\n"
            "15. التعامل مع الأخطاء بلغة مهذبة ومختصرة.\n\n"

            "🚨 إجراءات السلامة:\n"
            "- لا يتم الإرسال أو التنفيذ إلا بطلب واضح وصريح.\n"
            "- جميع عمليات CRUD تتم على قاعدة البيانات الداخلية فقط.\n"
            "- CRM يُستخدم حصريًا لعرض/استخراج بيانات العملاء.\n"
            "- لا يُنفذ أي إجراء في حالة النية الغامضة أو نقص البيانات إلا بعد استيضاح المستخدم.\n"
            "- التحقق من البريد وجهة الإرسال.\n"
            "- المهنية واجبة في كل الردود.\n"
            "- تحقق دائم من أن عمليات قاعدة البيانات مقيدة بالبريد الإلكتروني للمستخدم.\n"
        ),
        expected_output=(
            "مخرجات مقتضبة حسب النية مع الاستفادة من الوكلاء الجدد:\n"
            "✅ نعم/لا: إجابة قصيرة.\n"
            "✅ الصياغة: النص فقط مع تحسينات من التحليل العميق.\n"
            "✅ الإرسال: تأكيد مختصر مع النص عند الحاجة.\n"
            "✅ قاعدة البيانات: نتيجة CRUD مرتبطة ببريد المستخدم مع نص تأكيد.\n"
            "✅ ملفات PDF/Word/Excel: رسالة تأكيد مع مسار الملف في مجلد 'files/'.\n"
            "✅ إدارة CRM: عرض أو استخراج بيانات العملاء فقط عند تصريح المستخدم.\n"
            "✅ استفسارات Siyadah: رد دقيق من القاعدة المعرفية.\n"
            "✅ استيضاح: سؤال مباشر لتحديد النية أو تزويد البيانات الناقصة.\n"
            "⚠️ لا ملخصات أو تعليقات إضافية إلا بطلب المستخدم.\n"
            "🔣 لغة الرد = لغة المستخدم.\n\n"
            "**معايير النجاح للمهام الرقمية:**\n"
            "- وجود رقم واضح عند التنفيذ\n"
            "- نص تأكيد بلغة المستخدم\n"
            "- عند تحقق هذا التنسيق، تعتبر المهمة مكتملة\n\n"
            "🧠 **الميزات الجديدة المتاحة:**\n"
            "- فهم أعمق للطلبات المعقدة\n"
            "- ذاكرة مستمرة للمحادثات السابقة\n"
            "- تخطيط استراتيجي للتنفيذ الأمثل\n"
            "- شخصنة محسنة بناءً على السياق"
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
    mgr = manager_agent(llm_obj)

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
            "user_email": user_email
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
    test_manager = manager_agent(llm_obj)
    
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
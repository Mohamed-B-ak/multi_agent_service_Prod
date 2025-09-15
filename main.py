import os
import time
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
from langdetect import detect
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


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

# Request body model for the user input prompt
class UserPromptRequest(BaseModel):
    prompt: str
    user_email: str = "mohamed.ak@d10.sa"  # Optional field
    context: list = []      # Optional field with default empty list
# Crew agent workers
def get_workers(user_email, user_language, knowledge_base):
    """
    Initialize and return all worker agents.
    """
    llm_obj = get_llm()
    return [
        understanding_agent(llm_obj),
        content_agent(llm_obj, user_language),
        email_agent(llm_obj, user_email, user_language),
        whatsapp_agent(llm_obj, user_email, user_language),
        caller_agent(llm_obj, user_language),
        code_agent(llm_obj, user_language),  # <-- new code generation agent
        db_agent(llm_obj, user_email, user_language),
        siyadah_helper_agent(llm_obj, user_language),
        web_analyser_agent(llm_obj, user_language),
        knowledge_enhancer_agent(llm_obj, knowledge_base, user_language)
    ]

# Task for understanding and executing the user's request
def get_understand_and_execute_task():
    """
    تعريف وإرجاع المهمة لفهم وتنفيذ موجهات المستخدم، مع استخدام السياق داخليًا فقط إن كان ذا صلة.
    النظام الآن يتضمن وكيل تعزيز المحتوى (Knowledge-Enhanced Content Agent) ليتأكد من أن الصياغة
    متوافقة مع قاعدة المعرفة الخاصة بالشركة قبل الإرسال.
    """

    return Task(
        description=(
            "أنت تدير نظام ذكاء اصطناعي للتواصل والبرمجة قادر على:\n"
            "1. إنشاء محتوى البريد الإلكتروني: صياغة محتوى بريد إلكتروني احترافي (دون الإرسال) "
            "باستخدام أخصائي المحتوى + وكيل تعزيز المحتوى (Knowledge-Enhanced Content Agent).\n"
            "2. عمليات البريد الإلكتروني: إرسال الرسائل الإلكترونية، ولكن فقط إذا طلب المستخدم الإرسال بشكل صريح، "
            "ويجب تمرير المحتوى أولاً عبر وكيل تعزيز المحتوى.\n"
            "3. إنشاء محتوى واتساب: صياغة رسائل واتساب (دون الإرسال) "
            "باستخدام أخصائي المحتوى + وكيل تعزيز المحتوى.\n"
            "4. عمليات واتساب: إرسال رسائل واتساب، ولكن فقط إذا طلب المستخدم الإرسال بشكل صريح، "
            "ويجب تمرير المحتوى أولاً عبر وكيل تعزيز المحتوى.\n"
            "5. المكالمات الصوتية: إنشاء نص سكربت مبدئي باستخدام أخصائي المحتوى، "
            "ثم تحسينه عبر وكيل تعزيز المحتوى قبل التنفيذ.\n"
            "6. إنشاء كود بايثون: إنشاء كود بايثون نظيف وصحيح وفعال.\n"
            "7. العمليات على قاعدة البيانات: تنفيذ عمليات CRUD على MongoDB (إنشاء، قراءة، تحديث، حذف)، "
            "مع التأكيد أن *جميع العمليات يجب أن تكون مقيّدة ببريد المستخدم {user_email}* "
            "من خلال أحد الحقول (createdBy, createdByEmail, userEmail) لضمان العزل بين المستخدمين.\n"
            "8. أسئلة واستفسارات حول منصة Siyadah: إذا كانت النية استفسار أو مساعدة، تحقق من وكيل المساعد الذكي "
            "(Siyadah Intelligent Agent) أولاً للإجابة باستخدام قاعدة المعرفة.\n"
            "9. تحليل مواقع الويب: إذا كانت النية تتعلق بتحليل موقع ويب، استخدم وكيل Web Analysis Agent.\n\n"

            "🧠 سياسة استخدام السياق (داخليًا فقط):\n"
            "- يمكن استخدام {context_window} لفهم الموجه واستكمال النواقص عند الحاجة، لكن دون عرض أي تلخيص أو إحالات للسياق في الرد.\n"
            "- إذا تعارض السياق مع طلب المستخدم الصريح، يُتّبع طلب المستخدم.\n"
            "- لا يتم إضافة أي حواشٍ أو ملخصات إلا بطلب المستخدم.\n\n"

            "📝 وضع الإيجاز الصارم (Strict Concision):\n"
            "- أجب على قدر السؤال فقط دون أي إضافات.\n"
            "- أسئلة نعم/لا تُجاب بصيغة مقتضبة.\n\n"

            "طلب المستخدم: {user_prompt}\n\n"

            "التوجيه الذكي:\n"
            "📧 إذا كان النية = 'صياغة بريد إلكتروني' → أخصائي المحتوى + وكيل تعزيز المحتوى\n"
            "📧 إذا كان النية = 'إرسال بريد إلكتروني' → أخصائي المحتوى + وكيل تعزيز المحتوى + أخصائي البريد الإلكتروني\n"
            "📱 إذا كان النية = 'صياغة واتساب' → أخصائي المحتوى + وكيل تعزيز المحتوى\n"
            "📱 إذا كان النية = 'إرسال واتساب' → أخصائي المحتوى + وكيل تعزيز المحتوى + أخصائي واتساب\n"
            "☎️ إذا كان النية = 'صياغة مكالمة' → أخصائي المحتوى + وكيل تعزيز المحتوى\n"
            "☎️ إذا كان النية = 'إجراء مكالمة' → أخصائي المحتوى + وكيل تعزيز المحتوى + أخصائي المكالمات\n"
            "💻 إذا كان النية = 'إنشاء كود' → مولد كود بايثون\n"
            "🗂️ إذا كان النية = 'عمليات قاعدة بيانات' → أخصائي قاعدة البيانات\n"
            "🌐 إذا كان النية = 'تحليل موقع ويب' → وكيل Web Analysis Agent\n"
            "❓ إذا كانت النية = 'استفسار' أو 'مساعدة' → تحقق من وكيل المساعد الذكي (Siyadah Intelligent Agent) أولاً\n"
            "🔄 إذا كانت هناك نوايا متعددة → التنسيق بين الوكلاء\n"
            "❓ إذا كانت النية غير واضحة → الرد على استفسار عام.\n\n"

            "بروتوكول التنفيذ:\n"
            "1. الكشف عن لغة إدخال المستخدم.\n"
            "2. تحليل نية المستخدم باستخدام وكيل الفهم.\n"
            "3. الرد بنفس لغة/لهجة المستخدم.\n"
            "4. في *الصياغة*: يولد المحتوى عبر أخصائي المحتوى ثم يحسّنه وكيل تعزيز المحتوى.\n"
            "5. في *الإرسال*: صياغة + تعزيز المحتوى ثم تمريره لوكيل القناة المناسب.\n"
            "6. في *الكود*: ولّد كود بايثون نظيف.\n"
            "7. في *قاعدة البيانات*: نفّذ العمليات بعد التحقق من قيود البريد الإلكتروني.\n"
            "8. في *تحليل المواقع*: استخدم وكيل Web Analysis Agent للتقرير.\n"
            "9. في استفسارات Siyadah: تحقق أولاً من وكيل المساعد الذكي.\n"
            "10. الأسئلة المباشرة: أجب بإيجاز شديد.\n"
            "11. تأكيد فقط عند أفعال التنفيذ.\n"
            "12. تعامل مع الأخطاء بلطف وباختصار.\n\n"

            "إجراءات السلامة:\n"
            "- لا ترسل إلا بطلب صريح.\n"
            "- تحقق من تفاصيل الاتصال قبل الإرسال.\n"
            "- حافظ على المهنية.\n"
            "- تأكد من صحة أوامر قاعدة البيانات وربطها ببريد المستخدم.\n"
        ),
        expected_output=(
            "مخرجات مقتضبة وفق السؤال:\n"
            "✅ نعم/لا: إجابة قصيرة.\n"
            "✅ الصياغة: النص المطلوب فقط.\n"
            "✅ الإرسال: تأكيد قصير + المحتوى عند الحاجة.\n"
            "✅ الكود: كود بايثون فقط.\n"
            "✅ قاعدة البيانات: النتيجة المرتبطة ببريد المستخدم.\n"
            "✅ تحليل المواقع: تقرير منظم (Summary, Weaknesses, Recommendations).\n"
            "✅ أسئلة Siyadah: إجابة دقيقة من قاعدة المعرفة.\n"
            "⚠️ لا تدرج أي ملخصات أو ملاحظات إلا بطلب المستخدم.\n"
            "📣 لغة الاستجابة = لغة/لهجة إدخال المستخدم."
        ),
    )

# FastAPI endpoint to process the user prompt
@app.post("/process-prompt/")
async def process_prompt(request: UserPromptRequest):
    """
    FastAPI endpoint that receives a user prompt and processes it using the agent system.
    """
    user_prompt = request.prompt
    context_window = request.context
    # Initialize LLM and Manager
    llm_obj = get_llm()
    mgr = manager_agent(llm_obj)  # manager
    user_email = "mohamed.ak@d10.sa"
    # Detect user language
    try:
        user_language = detect(user_prompt)
    except Exception as e:
        user_language = "en"  # Default to English if detection fails
        print(f"Language detection failed: {e}")
    # Initialize agents
    print(f"Detected user language: {user_language}")
    try:
        client = MongoClient(os.getenv("MONGO_DB_URI"))
        db = client[os.getenv("DB_NAME")]
        collection = db["knowledgebases"]
        user_doc = collection.find_one({"createdByEmail": user_email})
        knowledge_base = user_doc['extractedContent']
    except:
        print("there is no knowledge base for the user : ", user_email)
        # Query for the user
        user_doc = collection.find_one({"createdByEmail": user_email})
    workers = get_workers(user_email, user_language, knowledge_base)

    # Define tasks
    understand_and_execute = get_understand_and_execute_task()

    # Create the crew with tasks
    crew = Crew(
        agents=workers,
        tasks=[understand_and_execute],
        process=Process.hierarchical,
        manager_agent=mgr,
        verbose=True,
    )
    
    # Run the process and time it
    start = time.time()
    try:
        # Execute the crew and get the final result
        final = crew.kickoff(inputs={"user_prompt": user_prompt, "context_window":context_window, "user_email": user_email})
        print("---------------------")
        print(final)
        print("---------------------")

        # Safely extract serializable text output
        if hasattr(final, "raw"):
            final_output = final.raw
        elif isinstance(final, dict) and "raw" in final:
            final_output = final["raw"]
        else:
            final_output = str(final)

        execution_time = time.time() - start
        return {"final_output": final_output, "execution_time": execution_time}

    except Exception as e:
        # Return an error message in case of failure
        raise HTTPException(status_code=500, detail=f"Error occurred: {str(e)}")


# Endpoint to serve the HTML interface
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

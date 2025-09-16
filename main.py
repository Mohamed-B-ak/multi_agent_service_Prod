import os
import time
import base64
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
from langdetect import detect
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

FOLDER_PATH = os.path.join(os.getcwd(), "files")  # ./files directory

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
        code_agent(llm_obj, user_language), 
        db_agent(llm_obj, user_email, user_language),
        siyadah_helper_agent(llm_obj, user_language),
        web_analyser_agent(llm_obj, user_language),
        knowledge_enhancer_agent(llm_obj, knowledge_base, user_language),
        file_creation_agent(llm_obj)
    ]

# Task for understanding and executing the user's request
from crewai import Task

def get_understand_and_execute_task():
    """
    تعريف وإرجاع المهمة لفهم وتنفيذ موجهات المستخدم، مع استخدام السياق داخليًا فقط إن كان ذا صلة.
    النظام الآن يتضمن وكلاء متخصصين، مثل وكيل تعزيز المحتوى، تحليل المواقع، إنشاء الكود، وصانع الملفات.
    """

    return Task(
        description=(
            "أنت تدير نظام ذكاء اصطناعي للتواصل والبرمجة قادر على:\n"
            "1. 📧 **محتوى البريد الإلكتروني**: صياغة بريد إلكتروني احترافي باستخدام أخصائي المحتوى + وكيل تعزيز المحتوى.\n"
            "2. 📤 **إرسال البريد الإلكتروني**: يتم فقط بطلب صريح، وبعد تمرير المحتوى لوكيل تعزيز المحتوى.\n"
            "3. 📱 **محتوى واتساب**: صياغة رسائل باستخدام أخصائي المحتوى + وكيل تعزيز المحتوى.\n"
            "4. 📲 **إرسال واتساب**: يتم فقط بطلب صريح، مع تمرير المحتوى عبر وكيل تعزيز المحتوى.\n"
            "5. ☎️ **نصوص المكالمات**: سكربت مبدئي من أخصائي المحتوى + تحسين عبر وكيل تعزيز المحتوى.\n"
            "6. 💻 **كود بايثون**: توليد كود نظيف وفعال.\n"
            "7. 🗂️ **عمليات قاعدة البيانات (MongoDB)**: تنفيذ CRUD مقيدة ببريد المستخدم {user_email}.\n"
            "8. 🌐 **تحليل مواقع الويب**: يتم باستخدام Web Analysis Agent لإخراج تقرير تحليلي.\n"
            "9. 🤖 **أسئلة واستفسارات Siyadah**: يتم تمريرها إلى وكيل المساعد الذكي Siyadah Intelligent Agent.\n"
            "10. 📄 **إنشاء ملفات PDF أو Word أو Excel**: باستخدام File Creator Agent، وحفظ الناتج في مجلد 'files/'.\n\n"

            "🧠 سياسة استخدام السياق (داخليًا فقط):\n"
            "- يمكن استخدام {context_window} لفهم الموجه واستكمال النواقص عند الحاجة، دون عرض تلخيص أو إحالات للسياق.\n"
            "- طلب المستخدم الصريح له الأولوية إذا تعارض مع السياق.\n\n"

            "📝 وضع الإيجاز الصارم (Strict Concision):\n"
            "- أجب على قدر السؤال فقط دون إضافات.\n"
            "- نعم/لا تُجاب باختصار.\n\n"

            "طلب المستخدم: {user_prompt}\n\n"

            "📌 التوجيه الذكي:\n"
            "📧 نية = 'صياغة بريد إلكتروني' → أخصائي المحتوى + وكيل تعزيز المحتوى\n"
            "📧 نية = 'إرسال بريد إلكتروني' → أخصائي المحتوى + وكيل تعزيز المحتوى + أخصائي البريد الإلكتروني\n"
            "📱 نية = 'صياغة واتساب' → أخصائي المحتوى + وكيل تعزيز المحتوى\n"
            "📱 نية = 'إرسال واتساب' → أخصائي المحتوى + وكيل تعزيز المحتوى + أخصائي واتساب\n"
            "☎️ نية = 'صياغة مكالمة' → أخصائي المحتوى + وكيل تعزيز المحتوى\n"
            "☎️ نية = 'إجراء مكالمة' → أخصائي المحتوى + وكيل تعزيز المحتوى + أخصائي المكالمات\n"
            "💻 نية = 'إنشاء كود' → مولد كود بايثون\n"
            "🗂️ نية = 'عمليات قاعدة بيانات' → أخصائي قاعدة البيانات\n"
            "🌐 نية = 'تحليل موقع ويب' → Web Analysis Agent\n"
            "📝 نية = 'إنشاء ملف PDF أو Word أو Excel' → File Creator Agent\n"
            "❓ نية = 'استفسار' أو 'مساعدة' → Siyadah Intelligent Agent\n"
            "🔄 نوايا متعددة → التنسيق بين الوكلاء\n"
            "❓ نية غير واضحة → الرد باستفسار عام.\n\n"

            "📜 بروتوكول التنفيذ:\n"
            "1. الكشف عن لغة المستخدم.\n"
            "2. تحليل النية باستخدام وكيل الفهم.\n"
            "3. الرد بنفس لغة المستخدم.\n"
            "4. في *الصياغة*: يولّد المحتوى ثم يُحسّن.\n"
            "5. في *الإرسال*: صياغة + تعزيز ثم تمرير لوكيل القناة.\n"
            "6. في *الكود*: توليد كود نظيف فقط.\n"
            "7. في *قاعدة البيانات*: تنفيذ بعد التحقق من قيود البريد.\n"
            "8. في *تحليل المواقع*: تقرير منظم.\n"
            "9. في *الملفات*: إنشاء الملف عبر File Creator Agent وحفظه في مجلد 'files/'.\n"
            "10. في استفسارات Siyadah: يتم استدعاء الوكيل المعرفي.\n"
            "11. الأسئلة المباشرة: إجابة مقتضبة.\n"
            "12. التأكيد فقط في حالة الأوامر التنفيذية.\n"
            "13. التعامل مع الأخطاء بلغة مهذبة ومختصرة.\n\n"

            "🚨 إجراءات السلامة:\n"
            "- لا يتم الإرسال أو التنفيذ إلا بطلب واضح وصريح.\n"
            "- التحقق من البريد وجهة الإرسال.\n"
            "- المهنية واجبة في كل الردود.\n"
            "- تحقق دائم من أن عمليات قاعدة البيانات مقيدة بالبريد الإلكتروني للمستخدم.\n"
        ),
        expected_output=(
            "مخرجات مقتضبة حسب النية:\n"
            "✅ نعم/لا: إجابة قصيرة.\n"
            "✅ الصياغة: النص فقط.\n"
            "✅ الإرسال: تأكيد مختصر مع النص عند الحاجة.\n"
            "✅ الكود: كود فقط.\n"
            "✅ قاعدة البيانات: نتيجة مرتبطة ببريد المستخدم.\n"
            "✅ تحليل المواقع: تقرير شامل (Summary, Weaknesses, Recommendations).\n"
            "✅ ملفات PDF/Word/Excel: رسالة تأكيد مع مسار الملف في مجلد 'files/'.\n"
            "✅ استفسارات Siyadah: رد دقيق من القاعدة المعرفية.\n"
            "⚠️ لا ملخصات أو تعليقات إضافية إلا بطلب المستخدم.\n"
            "📣 لغة الرد = لغة المستخدم."
        ),
    )

# FastAPI endpoint to process the user prompt
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

    # Initialize LLM and Manager
    llm_obj = get_llm()
    mgr = manager_agent(llm_obj)

    # Detect language
    try:
        user_language = detect(user_prompt)
    except Exception:
        user_language = "en"

    # Get knowledge base
    try:
        client = MongoClient(os.getenv("MONGO_DB_URI"))
        db = client[os.getenv("DB_NAME")]
        collection = db["knowledgebases"]
        user_doc = collection.find_one({"createdByEmail": user_email})
        knowledge_base = user_doc['extractedContent']
    except:
        knowledge_base = ""

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
        # Run agent process
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
        # Return JSON response
        # -----------------------
        return JSONResponse(content={
            "final_output": final_output,
            "execution_time": execution_time,
            "file_name": file_name,
            "file_content": file_data  # base64 encoded file (None if no file)
        })

    except Exception as e:
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

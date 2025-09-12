import os
import time
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from crewai import Crew, Process, Task, LLM
from agents.caller_agent import caller_agent
from agents.code_agent import code_agent
from agents.content_agent import content_agent
from agents.db_agent import db_agent
from agents.email_sender_agent import email_agent
from agents.manager_agent import manager_agent
from agents.understanding_agent import understanding_agent
from agents.whatsApp_sender import whatsapp_agent


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
    """
    Pydantic model for the user input prompt.
    """
    prompt: str

# Crew agent workers
def get_workers():
    """
    Initialize and return all worker agents.
    """
    llm_obj = get_llm()
    return [
        understanding_agent(llm_obj),
        content_agent(llm_obj),
        email_agent(llm_obj),
        whatsapp_agent(llm_obj),
        caller_agent(llm_obj),
        code_agent(llm_obj),  # <-- new code generation agent
        db_agent(llm_obj)
    ]

# Task for understanding and executing the user's request
def get_understand_and_execute_task():
    """
    تعريف وإرجاع المهمة لفهم وتنفيذ موجهات المستخدم.
    يجب على النظام معالجة ما يطلبه المستخدم بالضبط: صياغة، إرسال، أو إنشاء كود.
    ستكون الردود بلغة المستخدم المدخلة (أو اللهجة إذا تم اكتشافها).
    """
    
    return Task(
        description=( 
            "أنت تدير نظام ذكاء اصطناعي للتواصل والبرمجة قادر على:\n"
            "1. إنشاء محتوى البريد الإلكتروني: صياغة محتوى بريد إلكتروني احترافي (دون الإرسال).\n"
            "2. عمليات البريد الإلكتروني: إرسال الرسائل الإلكترونية، ولكن فقط إذا طلب المستخدم الإرسال بشكل صريح.\n"
            "3. إنشاء محتوى واتساب: صياغة رسائل واتساب (دون الإرسال).\n"
            "4. عمليات واتساب: إرسال رسائل واتساب، ولكن فقط إذا طلب المستخدم الإرسال بشكل صريح.\n"
            "5. المكالمات الصوتية: إجراء المكالمات مع نص سكربت، ولكن فقط إذا طلب المستخدم المكالمة بشكل صريح.\n"
            "6. إنشاء كود بايثون: إنشاء كود بايثون نظيف وصحيح وفعال.\n"
            "7. العمليات على قاعدة البيانات: تنفيذ عمليات CRUD على MongoDB (إنشاء، قراءة، تحديث، حذف).\n\n"
            
            "طلب المستخدم: {user_prompt}\n\n"
            
            "التوجيه الذكي:\n"
            "📧 إذا كان النية = 'صياغة بريد إلكتروني' → أخصائي المحتوى\n"
            "📧 إذا كان النية = 'إرسال بريد إلكتروني' → أخصائي المحتوى + أخصائي البريد الإلكتروني\n"
            "📱 إذا كان النية = 'صياغة واتساب' → أخصائي المحتوى\n"
            "📱 إذا كان النية = 'إرسال واتساب' → أخصائي المحتوى + أخصائي واتساب\n"
            "☎️ إذا كان النية = 'صياغة مكالمة' → أخصائي المحتوى\n"
            "☎️ إذا كان النية = 'إجراء مكالمة' → أخصائي المحتوى + أخصائي المكالمات\n"
            "💻 إذا كان النية = 'إنشاء كود' → مولد كود بايثون\n"
            "🗂️ إذا كان النية = 'عمليات قاعدة بيانات' → أخصائي قاعدة البيانات\n"
            "🔄 إذا كانت هناك نوايا متعددة → التنسيق بين الوكلاء\n"
            "❓ إذا كانت النية غير واضحة أو كانت سؤالًا عامًا → الرد على استفسار عام.\n\n"

            "بروتوكول التنفيذ:\n"
            "1. الكشف عن لغة إدخال المستخدم.\n"
            "2. تحليل نية المستخدم بدقة باستخدام وكيل الفهم.\n"
            "3. تحديد لغة إدخال المستخدم (التي قد تكون العربية أو الإنجليزية أو أي لغة أخرى) وضمان الرد بنفس اللغة.\n"
            "4. إذا طلب المستخدم *صياغة* → توليد المحتوى فقط، لا ترسله.\n"
            "5. إذا طلب المستخدم *إرسال* → صياغة المحتوى، ثم تمريره إلى الوكيل المناسب للتسليم.\n"
            "6. إذا طلب المستخدم *كود* → توليد كود بايثون باستخدام وكيل الكود.\n"
            "7. إذا طلب المستخدم *عمليات قاعدة بيانات* → تمرير الطلب إلى أخصائي قاعدة البيانات لتنفيذ العمليات على MongoDB.\n"
            "8. إذا كانت النية غير واضحة أو كانت سؤالًا عامًا → الرد على استفسار عام بشكل مناسب.\n"
            "9. توفير تأكيد واضح دائمًا:\n"
            "   - بالنسبة للصياغات → عرض المحتوى المصاغ.\n"
            "   - بالنسبة للإرسال → عرض المحتوى المصاغ مع تأكيد التسليم.\n"
            "   - بالنسبة لعمليات قاعدة البيانات → عرض النتائج أو تأكيد التنفيذ.\n"
            "10. التعامل مع الأخطاء بلطف مع شرح واضح.\n\n"

            "إجراءات السلامة:\n"
            "- لا ترسل رسائل بريد إلكتروني أو رسائل واتساب أو مكالمات إلا إذا طلب المستخدم بشكل صريح 'إرسال' أو ما يعادلها.\n"
            "- تحقق دائمًا من تفاصيل الاتصال (البريد الإلكتروني، أرقام الهاتف) قبل الإرسال.\n"
            "- تأكد من أن المحتوى المصاغ والمُرسل مهني وملائم للسياق.\n"
            "- قدم الصياغات بشكل منفصل عن تأكيدات التسليم.\n"
            "- تعامل مع الفشل مع خيارات لإعادة المحاولة.\n"
            "- تأكد من صحة أوامر قاعدة البيانات قبل تنفيذها لتجنب فقدان البيانات.\n"
        ),
        expected_output=( 
            "استجابة شاملة تتضمن:\n"
            "✅ المحتوى المصاغ (البريد الإلكتروني، واتساب، أو نص المكالمة) عند الطلب.\n"
            "✅ المحتوى المصاغ + تأكيد التسليم عند طلب المستخدم إرسال الرسالة بشكل صريح.\n"
            "✅ كود بايثون عند الطلب.\n"
            "✅ نتائج عمليات قاعدة البيانات عند الطلب.\n"
            "📊 تفاصيل المستلم، حالة الرسالة، أو شرح الكود عند الاقتضاء.\n"
            "⚠️ التعامل مع الأخطاء مع شرح واضح.\n"
            "🔄 الخطوات التالية أو التوصيات.\n"
            "📝 ملخص لجميع الإجراءات المتخذة.\n\n"
            "📣 ملاحظة: لغة الاستجابة تعتمد على لغة إدخال المستخدم أو اللهجة."
        ),
    )



# FastAPI endpoint to process the user prompt
@app.post("/process-prompt/")
async def process_prompt(request: UserPromptRequest):
    """
    FastAPI endpoint that receives a user prompt and processes it using the agent system.
    """
    user_prompt = request.prompt

    # Initialize LLM and Manager
    llm_obj = get_llm()
    mgr = manager_agent(llm_obj)  # manager

    # Initialize agents
    workers = get_workers()

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
        final = crew.kickoff(inputs={"user_prompt": user_prompt})
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

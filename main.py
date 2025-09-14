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
from agents.siyadah_helper_agent import siyadah_helper_agent
from agents.web_analyser_agent import web_analyser_agent
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
def get_workers(user_language):
    """
    Initialize and return all worker agents.
    """
    llm_obj = get_llm()
    return [
        understanding_agent(llm_obj),
        content_agent(llm_obj, user_language),
        email_agent(llm_obj, user_language),
        whatsapp_agent(llm_obj, user_language),
        caller_agent(llm_obj, user_language),
        code_agent(llm_obj, user_language),  # <-- new code generation agent
        db_agent(llm_obj, user_language),
        siyadah_helper_agent(llm_obj, user_language),
        web_analyser_agent(llm_obj, user_language),
    ]

# Task for understanding and executing the user's request
def get_understand_and_execute_task():
    """
    تعريف وإرجاع المهمة لفهم وتنفيذ موجهات المستخدم، مع استخدام السياق داخليًا فقط إن كان ذا صلة.
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
            "7. العمليات على قاعدة البيانات: تنفيذ عمليات CRUD على MongoDB (إنشاء، قراءة، تحديث، حذف)،"
            " مع التأكيد أن *جميع العمليات يجب أن تكون مقيّدة ببريد المستخدم {user_email}* لضمان العزل بين المستخدمين.\n"
            "8. أسئلة واستفسارات حول منصة Siyadah: إذا كانت النية استفسار أو مساعدة، يجب التحقق من وكيل المساعد الذكي (Siyadah Intelligent Agent) أولاً للإجابة باستخدام قاعدة المعرفة، وإذا لم تكن الإجابة مقنعة، أجب بشكل عام.\n"
            "9. تحليل مواقع الويب: إذا كانت النية تتعلق بتحليل موقع ويب، استخدم وكيل Web Analysis Agent لإجراء ما يلي:\n"
            "   - جمع محتوى الموقع\n"
            "   - تحليل نقاط القوة والضعف\n"
            "   - تقديم ملخص وتوصيات\n"
            "   - صياغة النتائج وفقًا لطلب المستخدم\n\n"
            "🧠 سياسة استخدام السياق (داخليًا فقط):\n"
            "- يمكن استخدام {context_window} لفهم الموجه واستكمال النواقص عند الحاجة، لكن دون عرض أي تلخيص أو إحالات للسياق في الرد.\n"
            "- إذا تعارض السياق مع طلب المستخدم الصريح، يُتّبع طلب المستخدم.\n"
            "- لا يتم إضافة أي حواشٍ، ملاحظات، أو «ملخص استخدام السياق» في المخرجات مالم يطلب المستخدم ذلك صراحةً.\n\n"

            "📝 وضع الإيجاز الصارم (Strict Concision):\n"
            "- أجب على قدر السؤال فقط دون أي إضافات.\n"
            "- أسئلة نعم/لا تُجاب بصيغة مقتضبة.\n"
            "- لا تُدرج معرفات أو تفاصيل إضافية ما لم يطلبها المستخدم صراحةً.\n\n"

            "طلب المستخدم: {user_prompt}\n\n"

            "التوجيه الذكي:\n"
            "📧 إذا كان النية = 'صياغة بريد إلكتروني' → أخصائي المحتوى\n"
            "📧 إذا كان النية = 'إرسال بريد إلكتروني' → أخصائي المحتوى + أخصائي البريد الإلكتروني\n"
            "📱 إذا كان النية = 'صياغة واتساب' → أخصائي المحتوى\n"
            "📱 إذا كان النية = 'إرسال واتساب' → أخصائي المحتوى + أخصائي واتساب\n"
            "☎️ إذا كان النية = 'صياغة مكالمة' → أخصائي المحتوى\n"
            "☎️ إذا كان النية = 'إجراء مكالمة' → أخصائي المحتوى + أخصائي المكالمات\n"
            "💻 إذا كان النية = 'إنشاء كود' → مولد كود بايثون\n"
            "🗂️ إذا كان النية = 'عمليات قاعدة بيانات' → أخصائي قاعدة البيانات (مع تقييد النتائج ببريد المستخدم)\n"
            "🌐 إذا كان النية = 'تحليل موقع ويب' → وكيل Web Analysis Agent\n"
            "❓ إذا كانت النية = 'استفسار' أو 'مساعدة' → تحقق من وكيل المساعد الذكي(Siyadah Intelligent Agent) أولاً\n"
            "🔄 إذا كانت هناك نوايا متعددة → التنسيق بين الوكلاء\n"
            "❓ إذا كانت النية غير واضحة → الرد على استفسار عام.\n\n"

            "بروتوكول التنفيذ:\n"
            "1. الكشف عن لغة إدخال المستخدم.\n"
            "2. تحليل نية المستخدم باستخدام وكيل الفهم مع الاستفادة من السياق داخليًا دون ذكره.\n"
            "3. الرد بنفس لغة/لهجة المستخدم.\n"
            "4. في *الصياغة*: ولِّد المحتوى فقط دون إرساله.\n"
            "5. في *الإرسال*: صِغ المحتوى ثم مرّره للوكيل المناسب بعد التحقق من بيانات التواصل.\n"
            "6. في *الكود*: ولِّد كود بايثون نظيفًا.\n"
            "7. في *قاعدة البيانات*: نفّذ عمليات MongoDB بعد التحقق من الأوامر، مع ضمان أن الاستعلامات والنتائج مرتبطة ببريد المستخدم {user_email}.\n"
            "8. في *تحليل مواقع الويب*: استخدم Web Analysis Agent لتوليد تقرير شامل (ملخص، نقاط ضعف، توصيات) وفق طلب المستخدم.\n"
            "9. في الأسئلة أو الاستفسارات حول Siyadah: إذا كانت النية استفسار أو مساعدة، تحقق أولاً من وكيل المساعد الذكي للإجابة بدقة بناءً على قاعدة المعرفة.\n"
            "10. في الأسئلة المباشرة (نعم/لا/حقائق): أجب بإيجاز شديد.\n"
            "11. قدّم تأكيدًا واضحًا فقط عند أفعال التنفيذ.\n"
            "12. تعامل مع الأخطاء بلطف وبجمل قليلة ومباشرة.\n\n"

            "إجراءات السلامة:\n"
            "- لا ترسل بريد/واتساب/مكالمات إلا بطلب صريح.\n"
            "- تحقّق من تفاصيل الاتصال قبل الإرسال.\n"
            "- حافظ على مهنية المحتوى وملاءمته للسياق.\n"
            "- تحقق من صحة أوامر قاعدة البيانات لتجنب فقدان البيانات.\n"
            "- جميع استعلامات قاعدة البيانات يجب أن تكون مقيّدة ببريد المستخدم {user_email}."
        ),
        expected_output=(
            "مخرجات مقتضبة وفق السؤال:\n"
            "✅ في أسئلة نعم/لا: إجابة قصيرة فقط.\n"
            "✅ في الصياغة: النص المطلوب فقط دون شروح إضافية.\n"
            "✅ في الإرسال: تأكيد الإرسال بجملة قصيرة + المحتوى إذا لزم.\n"
            "✅ في الكود: كود بايثون فقط.\n"
            "✅ في قاعدة البيانات: النتيجة المطلوبة فقط (مرتبطة ببريد المستخدم).\n"
            "✅ في تحليل مواقع الويب: تقرير منظم يشمل Summary, Weaknesses, Recommendations.\n"
            "✅ في الأسئلة حول Siyadah: إجابة دقيقة وواضحة باستخدام قاعدة المعرفة.\n"
            "⚠️ لا تُعرض أي «ملخص استخدام السياق» أو ملاحظات تفسيرية إلا بطلب صريح من المستخدم.\n"
            "📣 لغة الاستجابة تعتمد على لغة إدخال المستخدم أو اللهجة."
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
    # Detect user language
    try:
        user_language = detect(user_prompt)
    except Exception as e:
        user_language = "en"  # Default to English if detection fails
        print(f"Language detection failed: {e}")
    # Initialize agents
    print(f"Detected user language: {user_language}")
    workers = get_workers(user_language)

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
    user_email = "mohamed.ak@d10.sa"
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

from crewai import Agent
from Tools.whatsApp_tools import WhatsAppTool

def whatsapp_agent(llm_obj, user_email, user_language="en") -> Agent:
    goal_text = (
        f"إرسال رسائل واتساب **فقط عندما تكون جميع المعلومات متوفرة**: المستلم، الرسالة، والطلب الصريح من المستخدم. "
        f"إذا كانت أي معلومات ناقصة، لا ترسل أي شيء - بدلاً من ذلك، أخبر المستخدم ما هو المطلوب. "
        f"تذكر: أنت لست مساعد استفسار، أنت مختص إرسال فقط. "
        f"استخدم {user_language} حصرياً في جميع الردود."
    )

    backstory_text = (
        f"أنت خبير إرسال رسائل واتساب محترف يفهم متى يرسل ومتى لا يرسل. "
        f"مبدأك الأساسي: **لا إرسال بدون معلومات كاملة**. "
        f"عندما تتلقى طلباً ناقصاً مثل 'أطلق حملة واتساب' بدون تفاصيل، "
        f"لا تحاول إرسال أي رسالة - أخبر المستخدم أنك تحتاج: "
        f"١. قائمة أرقام الهواتف المستهدفة "
        f"٢. محتوى الرسالة "
        f"٣. تأكيد صريح للإرسال "
        f"أنت مختص تنفيذ، ليس مختص استشارة أو استفسار."
    )

    return Agent(
        role="مختص إرسال واتساب",
        goal=goal_text,
        backstory=backstory_text,
        tools=[WhatsAppTool(user_email=user_email)],
        allow_delegation=False,
        llm=llm_obj,
        verbose=True,
        max_retry_limit=1,
    )
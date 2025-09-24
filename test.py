from crewai import Agent, Task, Crew, Process
from Tools.whatsApp_tools import WhatsAppTool
from Tools.emailtest import MailerSendTool


def reply_agent(llm_obj, user_email, user_language="en") -> Agent:
    """
    Agent that generates and sends replies to customers
    on the same channel (WhatsApp or Email).
    """
    return Agent(
        role="Customer Reply Specialist",
        goal=(
            "Read the latest customer message and conversation history, "
            "generate a polite, professional reply in the same language, "
            "and send it back through the same channel (WhatsApp or Email)."
        ),
        backstory=(
            "You are the final voice of the company. "
            "On WhatsApp, you keep responses short, helpful, and friendly. "
            "On Email, you keep responses structured, formal, and professional. "
            "Always respect customer tone, be context-aware, and maintain consistency."
        ),
        allow_delegation=False,
        llm=llm_obj,
        tools=[
            WhatsAppTool(user_email=user_email),
            MailerSendTool(user_email=user_email),
        ],
        verbose=True,
    )


def get_reply_task(
    channel: str,
    customer_id: str,
    last_message: str,
    history: list,
    subject: str = "Customer Support"
) -> Task:
    """
    Create a task for replying to a customer depending on the channel.
    """
    history_text = "\n".join(
        [f"{msg['sender']}: {msg['message']}" for msg in history]
    )

    if channel.lower() == "whatsapp":
        return Task(
            description=(
                f"📱 WhatsApp message from `{customer_id}`:\n\n"
                f"Latest message: {last_message}\n\n"
                f"Conversation history:\n{history_text}\n\n"
                "Task:\n"
                "1. Generate a short, friendly, helpful reply in the same language.\n"
                "2. Send it with `WhatsAppTool(to_number, message)`.\n"
                "3. Keep it polite, professional, and context-aware."
            ),
            expected_output=f"✅ WhatsApp reply sent to {customer_id}"
        )

    elif channel.lower() == "email":
        return Task(
            description=(
                f"📧 Email from `{customer_id}`:\n\n"
                f"Latest message: {last_message}\n\n"
                f"Conversation history:\n{history_text}\n\n"
                "Task:\n"
                "1. Generate a structured, professional reply in the same language.\n"
                f"2. Send it with `MailerSendTool(to_email, subject, message)` (subject: {subject}).\n"
                "3. Ensure reply is polite, professional, and context-aware."
            ),
            expected_output=f"✅ Email reply sent to {customer_id}"
        )

    else:
        raise ValueError(f"Unsupported channel: {channel}")


def run_reply_crew(
    llm_obj,
    user_email,
    user_language,
    channel,
    customer_id,
    last_message,
    history,
    subject="Customer Support"
):
    """
    Orchestrates the reply process:
    - Reads message + history
    - Generates reply
    - Sends via correct tool
    """
    agent = reply_agent(llm_obj, user_email, user_language)
    task = get_reply_task(channel, customer_id, last_message, history, subject)

    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff(inputs={
        "channel": channel,
        "customer_id": customer_id,
        "last_message": last_message,
        "history": history,
        "subject": subject,
        "user_email": user_email,
    })

    return result.raw if hasattr(result, "raw") else str(result)


from main import get_llm


llm_obj = get_llm()

history = [
    {"sender": "customer", "message": "Hi, I need help with my order."},
    {"sender": "agent", "message": "Sure, could you share your order ID?"},
    {"sender": "customer", "message": "It’s #12345"},
]

# WhatsApp
print(run_reply_crew(
    llm_obj,
    user_email="mohamed.ak@d10.sa",
    user_language="en",
    channel="whatsapp",
    customer_id="+21655571368",
    last_message="Thanks, can you tell me the status?",
    history=history
))

# Email
print(run_reply_crew(
    llm_obj,
    user_email="mohamed.ak@d10.sa",
    user_language="en",
    channel="email",
    customer_id="customer@example.com",
    last_message="Can you please confirm shipping details?",
    history=history,
    subject="Order Inquiry"
))

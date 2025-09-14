from crewai import Agent
from Tools.whatsApp_tools import WhatsAppTool

def whatsapp_agent(llm_obj, user_language="en") -> Agent:
    """
    WhatsApp agent that sends messages using WhatsAppTool,
    respecting the user's language and strict concision.

    Args:
        llm_obj: LLM instance to use for generation.
        user_language: The language code of the user's input ('en', 'ar', etc.)

    Returns:
        Agent instance
    """
    goal_text = (
        f"Send professional WhatsApp messages to phone numbers using the WhatsAppTool. "
        f"⚠️ Respond ONLY in the user's language: {user_language}. "
        f"Do NOT translate or switch languages. "
        f"Follow strict concision: confirm sending only when explicitly requested, "
        f"and provide content professionally."
    )

    backstory_text = (
        f"You are the WhatsApp Sender responsible for delivering messages via WhatsApp. "
        f"All outputs must strictly be in {user_language}, concise, professional, "
        f"and aligned with the user's explicit instructions. "
        f"Do not send messages unless the user explicitly requests it."
    )

    return Agent(
        role="WhatsApp Sender",
        goal=goal_text,
        backstory=backstory_text,
        tools=[WhatsAppTool()],
        allow_delegation=False,
        llm=llm_obj,
        verbose=True,
        max_retry_limit=1,
    )

from crewai import Agent
from Tools.email_tools import MailerSendTool

def email_agent(llm_obj, user_language="en") -> Agent:
    """
    Email agent that sends emails using the MailerSend tool,
    respecting the user's language and strict concision.

    Args:
        llm_obj: LLM instance to use for generation.
        user_language: The language code of the user's input ('en', 'ar', etc.)

    Returns:
        Agent instance
    """
    goal_text = (
        f"Send well-formed emails using the MailerSend tool. "
        f"⚠️ Respond ONLY in the user's language: {user_language}. "
        f"Do NOT translate or switch languages. "
        f"Follow strict concision: confirm sending only when requested, "
        f"and provide content in a professional manner."
    )

    backstory_text = (
        f"You are the Email Sender responsible for delivering messages via MailerSend. "
        f"All outputs must strictly be in {user_language}, concise, professional, "
        f"and aligned with the user's explicit instructions. "
        f"Do not send emails unless the user explicitly requests it."
    )

    return Agent(
        role="Email Sender",
        goal=goal_text,
        backstory=backstory_text,
        tools=[MailerSendTool()],
        allow_delegation=False,
        llm=llm_obj,
        verbose=True,
        max_retry_limit=1,
    )

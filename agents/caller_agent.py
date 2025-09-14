from crewai import Agent
from Tools.call_tools import CallTool

def caller_agent(llm_obj, user_language="en") -> Agent:
    """
    Caller agent that places brief calls using a script,
    respecting the user's language and strict concision.

    Args:
        llm_obj: LLM instance to use for generation.
        user_language: The language code of the user's input ('en', 'ar', etc.)

    Returns:
        Agent instance
    """
    goal_text = (
        f"Place brief calls using a provided script via CallTool. "
        f"⚠️ Respond ONLY in the user's language: {user_language}. "
        f"Do NOT translate or switch languages. "
        f"Follow strict concision: confirm the call only when explicitly requested, "
        f"and keep the dialogue professional and concise."
    )

    backstory_text = (
        f"You are the Caller responsible for delivering calls using CallTool. "
        f"All outputs must strictly be in {user_language}, concise, professional, "
        f"and aligned with the user's explicit instructions. "
        f"Do not place calls unless the user explicitly requests it."
    )

    return Agent(
        role="Caller",
        goal=goal_text,
        backstory=backstory_text,
        tools=[CallTool()],
        allow_delegation=False,
        llm=llm_obj,
        verbose=True,
        max_retry_limit=1,
    )

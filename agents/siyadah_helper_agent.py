# agents/siyadah_helper_agent.py
from crewai import Agent
from Tools.siyadah_helper_tool import SiyadahHelperTool

def siyadah_helper_agent(llm_obj, user_language="en") -> Agent:
    """
    Siyadah helper agent that answers questions about the Siyadah platform
    using the knowledge base, in the user's language.

    Args:
        llm_obj: LLM instance to use for generation.
        user_language: Language code of the user's input ('en', 'ar', etc.)

    Returns:
        Agent instance
    """
    goal_text = (
        "Answer any question about the Siyadah platform using the Siyadah knowledge base. "
        f"⚠️ Respond ONLY in the user's language: {user_language}. "
        "Do NOT translate or switch languages. "
        "If the knowledge base does not provide a clear answer, respond in general terms, "
        "concise and professional."
    )

    backstory_text = (
        "Expert in the Siyadah platform and user guide. "
        f"All answers must be strictly in {user_language}, concise, accurate, "
        "and based primarily on the knowledge base. "
        "Fallback to general explanation only if necessary."
    )

    return Agent(
        role="Siyadah Knowledge Expert",
        goal=goal_text,
        backstory=backstory_text,
        tools=[SiyadahHelperTool()],
        allow_delegation=False,
        llm=llm_obj,
        verbose=True,
        max_retry_limit=1,
    )

from crewai import Agent

def content_agent(llm_obj, user_language="en") -> Agent:
    """
    Content agent that drafts professional content in the user's language,
    respecting strict concision and channel requirements.

    Args:
        llm_obj: LLM instance to use for generation.
        user_language: The language code of the user's input ('en', 'ar', etc.)

    Returns:
        Agent instance
    """

    goal_text = (
        f"Draft clear, concise, professional content tailored to the channel and recipient. "
        f"⚠️ Respond ONLY in the user's language: {user_language}. "
        f"Do NOT translate or switch languages. "
        f"Follow strict concision: answer only what is requested, without extra explanations."
    )

    backstory_text = (
        f"You are a Content Specialist responsible for drafting emails, WhatsApp messages, or call scripts. "
        f"All outputs must strictly be in {user_language}, concise, professional, and tailored to the user's request. "
        f"Do not include system notes or summaries unless explicitly requested."
    )

    return Agent(
        role="Content Specialist",
        goal=goal_text,
        backstory=backstory_text,
        allow_delegation=False,
        llm=llm_obj,
        verbose=True,
        max_retry_limit=1,
    )

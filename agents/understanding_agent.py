from crewai import Agent

def understanding_agent(llm_obj, user_language="en") -> Agent:
    """
    Understanding agent that parses user prompts and identifies intent and entities,
    respecting the user's language.
    """
    goal_text = (
        "Parse the user's prompt to identify the relevant intent (e.g., 'send email', 'send whatsapp') "
        "and extract structured data (entities like names, emails, phone numbers). "
        f"⚠️ Respond ONLY in the user's language: {user_language}. "
        "Do NOT translate or switch languages."
    )

    backstory_text = (
        "Parses user input and identifies entities and intents. "
        f"All extracted information must strictly be represented in {user_language}."
    )

    return Agent(
        role="Understanding Agent",
        goal=goal_text,
        backstory=backstory_text,
        llm=llm_obj,
        allow_delegation=False,
        verbose=True,
        max_retry_limit=1,
    )

from crewai import Agent

def knowledge_enhancer_agent(llm_obj, knowledge_base_text: str, user_language="en") -> Agent:
    """
    Knowledge-Enhanced Content Agent that refines draft messages using the full company knowledge base.

    Args:
        llm_obj: LLM instance to use for generation.
        knowledge_base_text: Full company knowledge base as a string.
        user_language: The language code of the user's input ('en', 'ar', etc.)

    Returns:
        Agent instance
    """

    goal_text = (
        f"Enhance and refine draft content (emails, WhatsApp messages, or call scripts) "
        f"so that it is clear, concise, professional, and aligned with the company's knowledge base. "
        f"⚠️ Respond ONLY in the user's language: {user_language}. "
        f"Do NOT translate or switch languages. "
        f"Ground every refinement in the following company knowledge base:\n\n"
        f"{knowledge_base_text}\n\n"
        f"Always output only the improved content, without extra explanations."
        f"All answers must be strictly in {user_language}, concise, accurate, "
    )

    backstory_text = (
        f"You are a Knowledge-Enhanced Content Refiner. "
        f"Your responsibility is to take draft content and enrich it with insights "
        f"from the company's knowledge base. "
        f"Ensure the result is accurate, professional, concise, and perfectly aligned "
        f"with the company’s tone of voice and guidelines. "
        f"You must strictly respond in {user_language} and avoid adding system notes, "
        f"meta text, or process commentary. Only return the refined final content."
        f"All answers must be strictly in {user_language}, concise, accurate, "
    )

    return Agent(
        role="Knowledge-Enhanced Content Refiner",
        goal=goal_text,
        backstory=backstory_text,
        allow_delegation=False,
        llm=llm_obj,
        verbose=True,
        max_retry_limit=1,
    )

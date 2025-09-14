from crewai import Agent

def code_agent(llm_obj, user_language="en") -> Agent:
    """
    Python code generator agent that writes clean, correct, and efficient Python code,
    with comments and explanations in the user's language.

    Args:
        llm_obj: LLM instance to use for generation.
        user_language: The language code of the user's input ('en', 'ar', etc.)

    Returns:
        Agent instance
    """
    goal_text = (
        "Write clean, correct, and efficient Python code given user requirements. "
        f"Include helpful comments and explanations in the user's language ({user_language}). "
        "Ensure code follows best practices and runs without syntax errors."
    )

    backstory_text = (
        "An expert software engineer specializing in Python. "
        f"Capable of translating natural language requests into production-ready Python code, "
        f"with comments and explanations strictly in {user_language}, "
        "paying attention to clarity, maintainability, and correctness."
    )

    return Agent(
        role="Python Code Generator",
        goal=goal_text,
        backstory=backstory_text,
        allow_delegation=False,
        llm=llm_obj,
        verbose=True,
        max_retry_limit=2,
    )

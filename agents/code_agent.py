from crewai import Agent
from crewai import Agent



def code_agent(llm_obj) -> Agent:
    return Agent(
        role="Python Code Generator",
        goal=(
            "Write clean, correct, and efficient Python code given user requirements. "
            "Ensure code follows best practices, includes helpful comments, "
            "and runs without syntax errors."
        ),
        backstory=(
            "An expert software engineer specializing in Python. "
            "Capable of translating natural language requests into production-ready code, "
            "with attention to clarity and maintainability."
        ),
        allow_delegation=False,
        llm=llm_obj,
        verbose=True,
        max_retry_limit=2,
    )

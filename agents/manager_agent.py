from crewai import Agent
from crewai import Agent



def manager_agent(llm_obj) -> Agent:
    return Agent(
        role="Operations Manager",
        goal=(
            "Coordinate and delegate tasks to specialized agents. "
            "DO NOT execute tools directly - only delegate and validate results."
        ),
        backstory=(
            "Expert coordinator who delegates to specialists and validates outputs. "
            "Never executes communication tools directly."
        ),
        allow_delegation=True,  # CHANGED: Enable delegation
        llm=llm_obj,
        verbose=True,
        max_retry_limit=1,
        # DO NOT add tools here - manager should only delegate
    )   
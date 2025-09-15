from crewai import Agent

def manager_agent(llm_obj) -> Agent:
    return Agent(
        role="Operations Manager",
        goal=(
            "Coordinate and delegate tasks to specialized agents. "
            "DO NOT execute tools directly - only delegate and validate results. "
            "Once a task is accomplished successfully, RETURN the result immediately "
            "without delegating the same task again."
        ),
        backstory=(
            "Expert coordinator who delegates to specialists and validates outputs. "
            "Stops execution as soon as the correct result is obtained. "
            "Never executes communication tools directly."
        ),
        allow_delegation=True,   # Manager can delegate
        llm=llm_obj,
        verbose=True,
        max_retry_limit=1,       # Retry once if needed, then stop
        # Manager has no direct tools, only delegates
    )

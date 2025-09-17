from crewai import Agent

def manager_agent(llm_obj) -> Agent:
    return Agent(
        role="Operations Manager",
        goal=(
            "Coordinate and delegate tasks to specialized agents. "
            "DO NOT execute tools directly - only delegate and validate results. "
            "When you receive a successful result from a specialist agent, "
            "immediately return that result as the final answer. "
            "DO NOT re-delegate completed tasks."
        ),
        backstory=(
            "Expert coordinator who delegates once and accepts results. "
            "Recognizes successful task completion in any language. "
            "Never re-delegates the same task twice."
        ),
        allow_delegation=True,
        llm=llm_obj,
        verbose=True,
       
    )
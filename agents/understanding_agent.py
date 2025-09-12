from crewai import Agent
from crewai import Agent



def understanding_agent(llm_obj) -> Agent:
    return Agent(
        role="Understanding Agent",
        goal="Parse the user's prompt to identify the relevant intent (e.g., 'send email', 'send whatsapp') and return structured data.",
        backstory="Parses user input and identifies entities (e.g., names, contact info) and intents (e.g., 'send email', 'send whatsapp').",
        llm=llm_obj,
        allow_delegation=False,
        verbose=True,
        max_retry_limit=1,
    )
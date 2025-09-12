from crewai import Agent
from crewai import Agent



def content_agent(llm_obj) -> Agent:
    return Agent(
        role="Content Specialist",
        goal="Draft clear, concise, professional content tailored to the channel and recipient.",
        backstory="Writes emails/messages/call scripts given structured guidance.",
        allow_delegation=False,
        llm=llm_obj,
        verbose=True,
        max_retry_limit=1,
    )
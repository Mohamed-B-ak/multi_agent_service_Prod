from crewai import Agent
from crewai import Agent
from Tools.call_tools import *



def caller_agent(llm_obj) -> Agent:
    return Agent(
        role="Caller",
        goal="Place brief calls using a script.",
        backstory="Owns telephony last-mile delivery.",
        tools=[CallTool()],
        allow_delegation=False,
        llm=llm_obj,
        verbose=True,
        max_retry_limit=1,
    )
from crewai import Agent
from crewai import Agent
from Tools.whatsApp_tools import *


def whatsapp_agent(llm_obj) -> Agent:
    return Agent(
        role="WhatsApp Sender",
        goal="Send WhatsApp messages to phone numbers.",
        backstory="Owns WhatsApp last-mile delivery.",
        tools=[WhatsAppTool()],
        allow_delegation=False,
        llm=llm_obj,
        verbose=True,
        max_retry_limit=1,
    )

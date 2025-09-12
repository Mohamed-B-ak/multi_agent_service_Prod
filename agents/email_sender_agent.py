from crewai import Agent
from crewai import Agent
from Tools.email_tools import MailerSendTool


def email_agent(llm_obj) -> Agent:
    return Agent(
        role="Email Sender",
        goal="Send well-formed email using the MailerSend tool.",
        backstory="Owns last-mile delivery via email.",
        tools=[MailerSendTool()],
        allow_delegation=False,
        llm=llm_obj,
        verbose=True,
        max_retry_limit=1,
    )
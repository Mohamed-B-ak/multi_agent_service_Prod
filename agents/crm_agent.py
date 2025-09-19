# agents/crm_agent.py

from crewai import Agent
from Tools.hubspot_tools import HubSpotContactsTool
# from tools.salesforce_tools import SalesforceContactsTool   # future extension
# from tools.zoho_tools import ZohoContactsTool               # future extension

def crm_agent(llm_obj, user_email: str, user_language: str = "en") -> Agent:
    goal_text = (
        f"Provide comprehensive customer insights by seamlessly accessing and analyzing CRM data. "
        f"Transform raw customer data into actionable business intelligence that drives better relationships. "
        f"Ensure data accuracy and provide context-rich customer profiles in {user_language}."
    )

    backstory_text = (
        f"You are a customer relationship management expert with deep understanding of sales processes "
        f"and customer lifecycle management. You excel at connecting data points to reveal customer insights, "
        f"identifying opportunities, and providing the intelligence needed for meaningful customer interactions. "
        f"Your expertise spans multiple CRM platforms and you're skilled at data interpretation."
    )

    return Agent(
        role="Customer Intelligence Specialist",
        goal=goal_text,
        backstory=backstory_text,
        tools=[HubSpotContactsTool(user_email=user_email)],
        allow_delegation=False,
        llm=llm_obj,
        verbose=True,
        max_retry_limit=1,
    )

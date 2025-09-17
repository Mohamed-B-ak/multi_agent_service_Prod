# agents/crm_agent.py

from crewai import Agent
from Tools.hubspot_tools import HubSpotContactsTool
# from tools.salesforce_tools import SalesforceContactsTool   # future extension
# from tools.zoho_tools import ZohoContactsTool               # future extension

def crm_agent(llm_obj, user_email: str, user_language: str = "en") -> Agent:
    """
    A CRM Agent that can interact with multiple CRM systems (HubSpot, Salesforce, Zoho, etc.)
    through their respective tools. The agent chooses the right CRM tool depending on the task.

    Args:
        llm_obj: LLM instance to use for reasoning and generation.
        user_email: The authenticated user’s email to fetch credentials from MongoDB.
        user_language: The language code of the user's input ('en', 'ar', etc.)

    Returns:
        Agent instance
    """
    goal_text = (
        f"Act as a unified CRM assistant across multiple systems (HubSpot, Salesforce, Zoho, etc.). "
        f"Retrieve, search, and summarize contact details, leads, and accounts. "
        f"⚠️ Always respond ONLY in the user's language: {user_language}. "
        f"Ensure accuracy, conciseness, and professionalism. "
        f"If a CRM has no data, explain clearly in {user_language}."
    )

    backstory_text = (
        f"You are the CRM Agent who consolidates access to multiple CRM platforms. "
        f"Your job is to fetch contacts, leads, and accounts across different tools. "
        f"You act as the single point of truth for CRM data. "
        f"You must never hallucinate information — only return verified data from CRM APIs."
    )

    return Agent(
        role="CRM Agent",
        goal=goal_text,
        backstory=backstory_text,
        tools=[HubSpotContactsTool(user_email=user_email)],
        allow_delegation=False,
        llm=llm_obj,
        verbose=True,
        max_retry_limit=1,
    )

from crewai import Crew, Process
from utils import get_llm
from .tasks import get_customer_service_task
from agents.email_sender_agent import email_agent
from agents.whatsApp_sender import whatsapp_agent
from agents.customer_service_agent import unified_customer_service_agent

def generate_reply(customer_id, channel, message, user_email, history):
    """
    Orchestrates CrewAI to generate a reply for customer service.
    - Builds the customer service task.
    - Loads agents (from agents/ folder).
    - Runs CrewAI with context and returns the reply.
    """
    # Initialize LLM and agents
    llm_obj = get_llm()
    workers = [
        unified_customer_service_agent(llm_obj, user_email)
    ]

    # Build the task
    task = get_customer_service_task(channel, message, history, customer_id)
    if channel == "whatsApp":
        task.agent = unified_customer_service_agent(llm_obj, user_email)
    # Create the crew
    crew = Crew(
        agents=workers,
        tasks=[task],
        verbose=True,
    )

    # Run the crew with inputs
    result = crew.kickoff(inputs={
        "user_prompt": message,
        "context_window": history,
        "user_email": customer_id,
    })

    return result.raw if hasattr(result, "raw") else str(result)

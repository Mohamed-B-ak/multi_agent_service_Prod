from crewai import Agent
from Tools.email_tools import MailerSendTool

def email_agent(llm_obj, user_email, user_language="en") -> Agent:
    goal_text = (
        f"Execute email communications with precision, ensuring deliverability and professional presentation. "
        f"Verify recipient details, optimize subject lines, and handle email delivery confirmations. "
        f"Maintain sender reputation and follow email best practices. Communicate in {user_language}."
    )

    backstory_text = (
        f"You are an email delivery specialist with deep knowledge of email systems, "
        f"deliverability optimization, and professional communication standards. "
        f"You understand the importance of sender reputation and recipient engagement. "
        f"You ensure every email sent reflects well on the sender and achieves its intended purpose."
    )

    return Agent(
        role="Email Delivery Specialist",
        goal=goal_text,
        backstory=backstory_text,
        tools=[MailerSendTool(user_email=user_email)],
        allow_delegation=False,
        llm=llm_obj,
        verbose=True,
        max_retry_limit=1,
    )
from crewai import Agent

def content_agent(llm_obj, user_language="en") -> Agent:
    goal_text = (
        f"Create compelling, audience-appropriate content for emails, WhatsApp messages, and call scripts. "
        f"Tailor tone, style, and messaging to match the intended recipient and communication channel. "
        f"Ensure all content is clear, actionable, and professionally crafted in {user_language}."
    )

    backstory_text = (
        f"You are a skilled content strategist with expertise in multi-channel communication. "
        f"You understand how message tone and structure should adapt across email, WhatsApp, and voice channels. "
        f"You craft messages that drive engagement and achieve business objectives while maintaining "
        f"authenticity and professionalism in {user_language}."
    )

    return Agent(
        role="Multi-Channel Content Strategist",
        goal=goal_text,
        backstory=backstory_text,
        allow_delegation=False,
        llm=llm_obj,
        verbose=True,
        max_retry_limit=1,
    )
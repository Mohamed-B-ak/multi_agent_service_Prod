# agents/context_memory_agent.py
from crewai import Agent
from Tools.context_memory_tools import ConversationMemoryTool, UserPatternAnalyzer, ContextRetrievalTool

def context_memory_agent(llm_obj, user_email: str, user_language="en") -> Agent:
    """
    وكيل ذاكرة السياق - يدير ويتذكر جميع التفاعلات والأنماط
    """
    goal_text = (
        f"Manage comprehensive conversational memory and context by:\n"
        f"1. Storing important interactions and outcomes\n"
        f"2. Recalling relevant historical context for current requests\n"
        f"3. Identifying user patterns and preferences\n"
        f"4. Connecting current requests with past conversations\n"
        f"5. Providing contextual insights to other agents\n"
        f"6. Learning user communication style and preferences\n"
        f"⚠️ Always operate in {user_language}\n"
        f"Focus on user {user_email} exclusively."
    )

    backstory_text = (
        f"You are the memory keeper and context specialist of the team. "
        f"You remember every important detail about user interactions, preferences, "
        f"and patterns. You help other agents provide more personalized and contextually "
        f"appropriate responses by sharing relevant memories and insights. "
        f"You understand the importance of continuity in conversations and relationships."
    )

    return Agent(
        role="Context Memory Specialist",
        goal=goal_text,
        backstory=backstory_text,
        tools=[
            #ConversationMemoryTool(user_email=user_email),
            #UserPatternAnalyzer(user_email=user_email),
            #ContextRetrievalTool(user_email=user_email),
        ],
        allow_delegation=False,
        llm=llm_obj,
        verbose=True,
        max_retry_limit=2,
    )
# agents/intent_analysis_agent.py
from crewai import Agent
from Tools.intent_analysis_tools import IntentAnalysisTool, EmotionalToneDetector, UrgencyAnalyzer

def intent_analysis_agent(llm_obj, user_language="en") -> Agent:
    """
    وكيل تحليل النوايا المتقدم - يحلل النوايا بعمق ودقة
    """
    goal_text = (
        f"Perform deep intent analysis by extracting:\n"
        f"1. Primary intent (main goal of the user)\n"
        f"2. Secondary intents (supporting or hidden goals)\n"
        f"3. Context modifiers (urgency, formality, scope)\n"
        f"4. Emotional tone and communication style\n"
        f"5. Implicit requirements and expectations\n"
        f"6. Multi-step task detection\n"
        f"⚠️ Always analyze and respond in {user_language}\n"
        f"Provide structured JSON analysis for other agents to use."
    )

    backstory_text = (
        f"You are a master of human communication analysis. "
        f"You can detect subtle nuances in language, understand implied meanings, "
        f"and recognize complex multi-layered requests. Your analysis helps the entire "
        f"team understand exactly what the user needs and how to deliver it perfectly. "
        f"You have expertise in cultural communication patterns, emotional intelligence, "
        f"and business communication contexts."
    )

    return Agent(
        role="Advanced Intent Analyzer",
        goal=goal_text,
        backstory=backstory_text,
        tools=[
            IntentAnalysisTool(),
            EmotionalToneDetector(),
            UrgencyAnalyzer(),
        ],
        allow_delegation=False,
        llm=llm_obj,
        verbose=True,
        max_retry_limit=2,
    )
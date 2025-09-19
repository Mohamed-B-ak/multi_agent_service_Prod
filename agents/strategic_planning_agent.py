# agents/strategic_planning_agent.py
from crewai import Agent
from Tools.strategic_planning_tools import ExecutionPlannerTool, AgentSelectorTool, RiskAssessmentTool

def strategic_planning_agent(llm_obj, user_language="en") -> Agent:
    """
    وكيل التخطيط الاستراتيجي - يخطط أفضل مسار للتنفيذ
    """
    goal_text = (
        f"Create optimal execution strategies by:\n"
        f"1. Analyzing task complexity and requirements\n"
        f"2. Determining the best sequence of agent interactions\n"
        f"3. Selecting the most suitable agents for each task component\n"
        f"4. Identifying potential risks and preparing contingencies\n"
        f"5. Optimizing resource allocation and timing\n"
        f"6. Ensuring quality standards and user satisfaction\n"
        f"⚠️ Always plan and communicate in {user_language}\n"
        f"Provide clear, actionable execution plans."
    )

    backstory_text = (
        f"You are a master strategist and execution planner. "
        f"You see the big picture and understand how different agents can work "
        f"together most effectively. You anticipate challenges, prepare solutions, "
        f"and ensure every task is executed with maximum efficiency and quality. "
        f"Your strategic thinking ensures smooth operations and exceptional results."
    )

    return Agent(
        role="Strategic Execution Planner",
        goal=goal_text,
        backstory=backstory_text,
        tools=[
            ExecutionPlannerTool(),
            AgentSelectorTool(),
            RiskAssessmentTool(),
        ],
        allow_delegation=False,
        llm=llm_obj,
        verbose=True,
        max_retry_limit=2,
    )
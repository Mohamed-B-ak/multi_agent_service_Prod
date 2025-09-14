import os
from crewai import Agent
from crewai_tools import WebsiteSearchTool, FileReadTool

def web_analyser_agent(llm_obj, user_language="en") -> Agent:
    """
    Web analysis agent that scrapes websites and generates structured reports
    in the user's language.

    Args:
        llm_obj: LLM instance to use for generation.
        user_language: Language code of the user's input ('en', 'ar', etc.)

    Returns:
        Agent instance
    """
    scraper_tool = WebsiteSearchTool()
    analyzer_tool = FileReadTool()

    goal_text = (
        "Scrape websites, extract textual content, and generate structured analysis "
        f"with summaries, weaknesses, and recommendations. "
        f"⚠️ Respond ONLY in the user's language: {user_language}. "
        "Do NOT translate or switch languages. Provide clear, concise, professional reports."
    )

    backstory_text = (
        "You are an expert in website analysis. "
        f"All reports must strictly be in {user_language}, including: Summary, Weaknesses, and Recommendations. "
        "Ensure clarity, organization, and professional presentation."
    )

    return Agent(
        name="WebAnalysisAgent",
        role="Web Scraping and Analysis Specialist",
        goal=goal_text,
        backstory=backstory_text,
        tools=[scraper_tool, analyzer_tool],
        allow_delegation=False,
        llm=llm_obj,
        verbose=True,
        max_retry_limit=1,
    )

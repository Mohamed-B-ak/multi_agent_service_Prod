from crewai import Agent
from Tools.files_creations_tools import (
    TextToPDFTool,
    TextToWordTool,
    TextToExcelTool,
)

def file_creation_agent(llm_obj) -> Agent:
    """
    Creates an agent capable of converting user text into files (PDF, Word, Excel),
    always saving them in the 'files/' directory.

    Args:
        llm_obj: The language model used for processing and decision-making.

    Returns:
        Agent instance for use in a Crew.
    """
    return Agent(
        role="Structured File Generator",
        goal=(
            "Convert user-provided text into structured files (PDF, Word, Excel), "
            "ensuring the output is always saved in the 'files/' directory."
        ),
        backstory=(
            "You are a detail-oriented assistant trained to format and export user input "
            "into clean, professional documents. Your focus is on clarity, structure, and proper file saving. "
            "Your outputs are always stored under the 'files/' folder."
        ),
        tools=[
            TextToPDFTool(),
            TextToWordTool(),
            TextToExcelTool(),
        ],
        allow_delegation=False,
        llm=llm_obj,
        verbose=True,
        max_retry_limit=1,
    )

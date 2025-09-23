"""
Planner method for task decomposition
"""

from crewai import Agent, Task, Crew
from typing import List, Dict

def planner(user_prompt: str, context: List[Dict] = None, llm_object = None) -> str:
    """
    Decomposes a user request into subtasks considering conversation context.
    
    Args:
        user_prompt: The current user request to decompose
        context: List of previous conversation messages with role, content, timestamp
        llm_object: The LLM instance to use for the agent
    
    Returns:
        String with decomposed tasks as a numbered list
    """
    
    # Create the decomposition agent
    decomposer = Agent(
        role="Task Decomposer with Context Understanding",
        goal="Understand user requests and break them into ONLY the necessary subtasks - no extras",
        backstory="""You are an expert at understanding user intent and decomposing ONLY what was requested.
        
        CRITICAL RULES:
        1. ONLY include tasks the user explicitly asked for
        2. If user says "prepare" or "draft" - DO NOT add sending steps
        3. If user says "send" - then include sending steps
        4. If user mentions "them" or references people from context - get their contacts FIRST
        5. Never add optional or helpful tasks the user didn't request
        
        Examples:
        - "جهزلي حملة ايميلات" = Only prepare/draft, NO sending
        - "أرسل لهم رسالة" = Get contacts + draft + send
        - "اكتب ايميل" = Only write, NO sending""",
        verbose=False,
        allow_delegation=False,
        llm=llm_object,
    )
    
    # Format context if provided
    context_str = ""
    if context:
        context_str = f"\n\nConversation Context:\n{context}\n"
    
    # Create the task
    task = Task(
        description=f"""{context_str}
        
        Current Request: '{user_prompt}'
        
        IMPORTANT: Use the conversation context above to understand what the user means.
        
        STRICT RULES - DO NOT ADD TASKS THE USER DIDN'T REQUEST:
        1. If user says "prepare/جهز" or "draft/اكتب" = ONLY create content, NO sending
        2. If user says "send/أرسل" = Include sending steps
        3. If user says "create campaign/حملة" without "send" = ONLY prepare, NO sending
        4. NEVER add helpful extras like "send" when not requested
        
        Critical Rules for References:
        - If sending to "them" or specific people from context, FIRST retrieve their contact information
        - If preparing content for general use (no specific recipients), NO need to get contacts
        
        Break down the request into subtasks and output a simple numbered list like:
        1. [Action] - [Who should do it]
        2. [Action] - [Who should do it]
        
        Consider these available agents:
        - Content Agent (drafts messages, emails, scripts)
        - Knowledge Enhancer Agent (improves and refines content)
        - Database Agent (MongoDB CRUD operations, gets customer data)
        - Email Agent (sends emails via MailerSend)
        - WhatsApp Agent (sends WhatsApp messages)
        - CRM Agent (extract/display customers/contacts saved in the CRM)
        - Caller Agent (makes phone calls with scripts)
        - File Creation Agent (creates PDF/Word/Excel files)
        - Web Analyser Agent (scrapes and analyzes websites)
        - Code Agent (generates Python code)
        - Siyadah Helper Agent (answers platform questions)
        
        IMPORTANT: when creating content using Content Agent, always enhance it using the Knowledge Enhancer Agent""",
        expected_output="A numbered list of subtasks with responsible agents based on the context and request",
        agent=decomposer
    )
    
    # Create and run the crew
    crew = Crew(
        agents=[decomposer],
        tasks=[task],
        verbose=False
    )
    
    # Execute and return result
    result = crew.kickoff()
    
    # Return the raw result if it's an object, otherwise return as string
    if hasattr(result, 'raw'):
        return result.raw
    return str(result)


# Example usage
if __name__ == "__main__":
    from dotenv import load_dotenv
    import os
    from crewai import LLM
    
    # Load environment
    load_dotenv()
    
    # Initialize LLM
    llm = LLM(
        model=os.getenv("OPENAI_MODEL", "gpt-4o"),
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.1,
        max_tokens=500,
    )
    
    # Example context
    context = [
        {'role': 'user', 'content': 'كم لدي من عميل في حسابي', 'timestamp': '2025-09-23T08:14:36.549Z'},
        {'role': 'assistant', 'content': 'لديك 4 عملاء في حسابك.', 'timestamp': '2025-09-23T08:14:36.549Z'},
        {'role': 'user', 'content': 'عطني أسمائهم', 'timestamp': '2025-09-23T08:15:48.442Z'},
        {'role': 'assistant', 'content': 'الأسماء هي: توفيق أنيس، بن نجمة سحر، دريدي هبة، وعكاشة محمد.', 'timestamp': '2025-09-23T08:15:48.442Z'}
    ]
    
    # Call the planner
    user_prompt = ""
    result = planner(user_prompt, context, llm)
    
    print("Decomposed Tasks:")
    print(result)
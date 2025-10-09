# agents/planner_agent.py
"""
Planner method for task decomposition with combined Knowledge-Based Content Agent
"""

from crewai import Agent, Task, Crew
from typing import List, Dict

def planner(user_prompt: str, context: List[Dict] = None, llm_object = None) -> str:
    """
    Decomposes a user request into subtasks considering conversation context.
    Now uses the combined Knowledge-Based Content Agent for all content creation.
    
    Args:
        user_prompt: The current user request to decompose
        context: List of previous conversation messages with role, content, timestamp
        llm_object: The LLM instance to use for the agent
    
    Returns:
        String with decomposed tasks as a numbered list
    """
    
    # Create the decomposition agent
    decomposer = Agent(
        role="Intelligent Task Analyzer",
        goal="""Understand what the user ACTUALLY wants and decompose it into the minimal necessary steps.
        
        CORE PRINCIPLE: Match user intent to system capability, not keywords to patterns.
        
        SYSTEM CAPABILITIES:
        1. Database Operations: Create, Read, Update, Delete, Count documents
        2. Content Creation: Draft/prepare messages for WhatsApp or Email  
        3. Communication: Send WhatsApp/Email (single or bulk)
        4. File Generation: Create PDF, Word, Excel files
        5. CRM Operations: Manage customer relationships
        6. Analysis: Web scraping, data analysis
        
        INTENT ANALYSIS:
        - If user wants a NUMBER (how many, count, total) → Use Count operation
        - If user wants to SEE data (show, list, display) → Use Read operation
        - If user wants to MODIFY data (add, update, delete) → Use appropriate CRUD operation
        - If user wants to COMMUNICATE (send, notify) → Check what's needed (content? recipients?) then send
        - If user wants TEXT (write, prepare, draft) → Create content without sending
        - If user wants FILES → Generate the requested file type
        
        CONTEXT INTELLIGENCE:
        - Check if data/content already exists in conversation before retrieving/creating
        - Recognize references ("it", "this", "them") to previous context
        - Skip redundant operations when information is already available""",
        
        backstory="""You are an AI that deeply understands user intent and system capabilities.
        
        Your thinking process:
        1. What is the user's END GOAL? (a number? data? an action? a file?)
        2. What's ALREADY AVAILABLE in context?
        3. What's the MINIMAL path to achieve this goal?
        
        You understand that:
        - "كم" or "how many" wants a COUNT, not a list
        - "أرسل" or "send" needs both CONTENT and RECIPIENTS
        - "أضف" or "add" needs CREATE operation
        - "احذف" or "delete" needs DELETE operation
        - "حدث" or "update" needs UPDATE operation
        - "اعرض" or "show" needs READ operation
        - "جهز" or "prepare" needs CONTENT CREATION only (no sending)
        
        But more importantly, you understand INTENT beyond keywords:
        - Someone asking about quantity wants a number
        - Someone asking to see something wants data
        - Someone asking for action wants execution
        
        Never overthink. Choose the simplest tool that directly answers the user's need.""",
        verbose=False,
        allow_delegation=False,
        llm=llm_object,
    )
    context_str = ""
    if context:
        context_str = f"\n\nConversation Context:\n{context}\n"
# Simplified task description
    task = Task(
        description=f"""
        Context: {context_str}
        User Request: '{user_prompt}'
        
        ANALYZE THE USER'S ACTUAL NEED:
        
        1. INTENT DETECTION:
        □ What does the user want as OUTPUT?
            - A number/count → Use: "Count documents - DB Agent"
            - View/see data → Use: "Read data - DB Agent"  
            - Add new data → Use: "Create document - DB Agent"
            - Modify existing → Use: "Update document - DB Agent"
            - Remove data → Use: "Delete document - DB Agent"
            - Message content → Use: "Create content - Marketing Agent"
            - Send messages → Use: "Send via WhatsApp/Email - Marketing Agent"
            - Generate file → Use: "Create file - File Agent"
        
        2. CONTEXT CHECK:
        □ Is the needed data already in the conversation?
        □ Is there prepared content that can be reused?
        □ Are there references to previous items ("it", "them", "this")?
        
        3. MINIMAL DECOMPOSITION:
        Only include steps that are ABSOLUTELY NECESSARY.
        
        Examples of correct decomposition:
        - "كم لدي من عميل" → "Count customers - DB Agent"
        - "أضف عميل اسمه أحمد" → "Create customer record - DB Agent"
        - "احذف العميل رقم 5" → "Delete customer by ID - DB Agent"
        - "أرسل رسالة للعملاء" → 
            Step 1: "Get customer contacts - DB Agent"
            Step 2: "Create message content - Marketing Agent"  
            Step 3: "Send bulk WhatsApp - Marketing Agent"
        - "جهز رسالة ترحيب" → "Create welcome message - Marketing Agent"
        - "أرسلها لهم" (if message exists in context) → 
            Step 1: "Get customer contacts - DB Agent"
            Step 2: "Send existing message - Marketing Agent"
        
        Output format:
        Return ONLY the necessary steps as:
        1. [Specific action] - [Agent]
        2. [Specific action] - [Agent]
        
        Or for single operations:
        [Specific action] - [Agent]
        
        Available Agents:
        - DB Agent: All database operations (CRUD, Count)
        - Marketing Agent: Content creation and sending (WhatsApp/Email)
        - Sales Agent: Personalized sales operations
        - File Agent: Generate PDF/Word/Excel files
        - CRM Agent: Customer relationship management
        """,
        
        expected_output="""The MINIMAL set of operations needed.
        Be specific about the operation type:
        - Don't say "database operation", say "Count documents" or "Read data"
        - Don't say "handle request", say exactly what to do
        - Each step must be actionable and specific""",
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
        model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
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
    user_prompt = "أرسل لهم رسالة ترحيب"
    result = planner(user_prompt, context, llm)
    
    print("Decomposed Tasks:")
    print(result)
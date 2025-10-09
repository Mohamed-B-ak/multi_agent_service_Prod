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
        role="Smart Task Decomposer with Context Analysis",
        goal="""Understand user requests and decompose them intelligently by checking context for both DATA and CONTENT.

        CONTEXT CHECKING RULES:
        1. Check for existing CONTACT DATA (phones, emails, names)
        2. Check for existing MESSAGE CONTENT (drafted messages, prepared campaigns)
        3. If data/content exists in context → SKIP creation/retrieval
        4. If data/content is missing → ADD necessary tasks
        5. Pay attention to references like "this message", "that content", "them"
        
        CONTENT REUSE RULES:
        1. If user previously asked to "prepare/draft" content → it exists in context
        2. If user now says "send it/this/that message" → use existing content
        3. If user says "send them the welcome message" and content exists → skip content creation
        4. Only create new content if explicitly requested or if no content exists
        
        DECOMPOSITION RULES:
        1. ONLY include tasks the user explicitly asked for
        2. Reuse what's already available in conversation
        3. If user says "prepare/draft" → NO sending steps
        4. If user says "send" → check what's needed (data? content?) then act
        5. Never add redundant or optional tasks""",

        backstory="""You are an expert at understanding context and avoiding redundant work.
        
        CRITICAL CONTEXT AWARENESS:
        
        FOR DATA:
        - Before adding "Retrieve phone numbers" → CHECK if phones are in conversation
        - Before adding "Retrieve emails" → CHECK if emails were shown
        - Before adding "Get customer data" → CHECK if data was displayed
        
        FOR CONTENT:
        - Before adding "Create message content" → CHECK if content was prepared
        - Before adding "Draft campaign" → CHECK if campaign text exists
        - Look for prepared messages, drafted emails, created content
        
        SMART EXAMPLES:
        
        Example 1 - Content Reuse:
        - User: "prepare a welcome message with 30% discount"
        - System: "✅ Message prepared: Welcome! Enjoy 30% off..."
        - User: "send it to all customers"
        → NO need to create content again, just: "Send existing message to customers"
        
        Example 2 - Data Reuse:
        - User: "show customer phones"
        - System: "+21653844063, +966555123456..."
        - User: "send them a message"
        → NO need to retrieve phones, they're in context
        
        Example 3 - Both Missing:
        - User: "send a promotional SMS to all customers"
        → Need both: 1) Get phone numbers 2) Create content 3) Send
        
        Example 4 - Content Exists, Data Missing:
        - User: "draft a discount offer"
        - System: "✅ Offer drafted: Special 50% discount..."
        - User: "send it to everyone"
        → Only need: 1) Get phone numbers 2) Send existing content
        
        Your strength: Recognizing what's already available vs what needs creating.""",
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
        
        🔍 CONTEXT ANALYSIS CHECKLIST:
        
        DATA CHECK:
        □ Are phone numbers in context? (Look for +XXX format)
        □ Are email addresses in context? (Look for @domain format)
        □ Are customer names/IDs in context?
        
        CONTENT CHECK:
        □ Is there a prepared/drafted message in recent context?
        □ Did user previously ask to "prepare", "draft", "write" content?
        □ Is there campaign text, offer details, or message content visible?
        □ Is user referencing "it", "this message", "that content"?
        
        📋 SMART DECOMPOSITION PATTERNS:
        
        Pattern 1 - Everything exists:
        User says "send it to them" + content exists + phones exist
        → Task: "Send [existing content] to [phones from context] - Marketing Agent"
        
        Pattern 2 - Content exists, data missing:
        User says "send this to all customers" + content exists + no phones
        → Task 1: "Retrieve customer phone numbers - DB Agent"
        → Task 2: "Send [existing content] to retrieved numbers - Marketing Agent"
        
        Pattern 3 - Data exists, content missing:
        User says "send them a welcome message" + phones exist + no content
        → Task 1: "Create welcome message content - Marketing Agent"
        → Task 2: "Send to [phones from context] - Marketing Agent"
        
        Pattern 4 - Nothing exists:
        User says "send discount SMS to customers" + no phones + no content
        → Task 1: "Retrieve customer phone numbers - DB Agent"
        → Task 2: "Create discount SMS content - Marketing Agent"
        → Task 3: "Send to retrieved numbers - Marketing Agent"
        
        Pattern 5 - Just preparation:
        User says "prepare a campaign message"
        → Task: "Create campaign message content - Marketing Agent"
        (NO sending, NO data retrieval)
        
        STRICT RULES:
        1. NEVER recreate content that's visible in the last 3 messages
        2. NEVER retrieve data that's already shown
        3. When user says "it/this/that" → find what they're referring to
        4. Be minimal - use what exists, create only what's missing
        
        Output format (only necessary tasks):
        1. [Action] - [Agent]
        2. [Action] - [Agent]
        
        Available agents:
        - Marketing Agent → create content, send messages
        - Sales Agent → personalized follow-ups
        - DB Agent → retrieve data (ONLY if not in context)
        
        Remember: Check context first! Don't recreate what exists!""",
        
        expected_output="""Minimal task list based on what's already available.
        - Content in context? → Skip content creation
        - Data in context? → Skip data retrieval  
        - Both exist? → Go straight to action
        - Neither exists? → Add both tasks first""",
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
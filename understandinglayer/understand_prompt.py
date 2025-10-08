"""
Simple Prompt Understanding Layer
A clean, straightforward layer for understanding user prompts with context
"""

import json
from openai import OpenAI
from typing import Dict, List, Optional
from datetime import datetime
import os
from dotenv import load_dotenv
import os
from crewai import LLM
    
    # Load environment
load_dotenv()

class SimplePromptUnderstanding:
    """Simple class to hold understanding results"""
    def __init__(self, data: dict):
        self.user_input= data.get("user_input")
        self.intent = data.get("intent", "unknown")
        self.meaning = data.get("meaning", "")
        self.tone = data.get("tone", "neutral")
        self.entities = data.get("entities", {})
        self.language = data.get("language", "en")
        self.dialect = data.get("dialect", "standard")  # NEW
        self.needs_clarification = data.get("needs_clarification", False)
        self.clarification_question = data.get("clarification_question", "")
        self.confidence = data.get("confidence", 0.7)
        self.urgency = data.get("urgency", "normal")
        self.context_references = data.get("context_references", {})
        self.response_type = data.get("response_type", "")
        self.selected_agents = data.get("selected_agents", [])
        

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "user_input": self.user_input,
            "intent": self.intent,
            "meaning": self.meaning,
            "tone": self.tone,
            "entities": self.entities,
            "language": self.language,
            "dialect": self.dialect,   # NEW
            "needs_clarification": self.needs_clarification,
            "clarification_question": self.clarification_question,
            "confidence": self.confidence,
            "urgency": self.urgency,
            "context_references": self.context_references,
            "response_type": self.response_type,
            "selected_agents": self.selected_agents


        }

class PromptUnderstandingLayer:
    """
    Simple layer to understand user prompts with context
    """
    
    def __init__(self, user_prompt, context,  api_key: str = None):
        """Initialize with OpenAI API key"""
        self.user_prompt= user_prompt
        self.context = context
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
    def understand(
        self, 
        model: str = "gpt-4o"
    ) -> SimplePromptUnderstanding:
        """
        Understand user prompt with context
        
        Args:
            user_prompt: The user's input
            context: Previous messages [{"role": "user/assistant", "content": "..."}]
            model: OpenAI model to use
            
        Returns:
            SimplePromptUnderstanding object
        """
        
        # Build the analysis prompt
        analysis_prompt = self._build_prompt(self.user_prompt, self.context)
        
        try:
            # Call OpenAI
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at understanding user requests. Analyze prompts and return JSON."
                    },
                    {
                        "role": "user",
                        "content": analysis_prompt
                    }
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            # Parse the response
            content = response.choices[0].message.content
            print(content)
            result = self._parse_json(content)
            print(result)
            # Return understanding object
            return SimplePromptUnderstanding(result)
            
        except Exception as e:
            print(f"Error: {e}")
            # Return basic understanding on error
            return SimplePromptUnderstanding({
                "intent": "unknown",
                "meaning": self.user_prompt,
                "needs_clarification": True,
                "clarification_question": "Could you please clarify your request?"
            })
    
    def _build_prompt(self, user_prompt: str, context: List[Dict]) -> str:
        """Build the analysis prompt (multi-agent aware)"""

        return f"""
                You are a conversation analyzer for Siyadah AI — a system that helps users manage campaigns, marketing, sales, data, and system operations.

                Your goal is to deeply understand what the user wants based on the current message and conversation context, 
                and decide which Siyadah AI agents must cooperate to fulfill the request.

                ---

                ### CONTEXT
                {context}

                ### CURRENT USER PROMPT
                "{user_prompt}"

                ---

                ### Perform the following structured analysis:

                1. **INTENT** – What is the user's main goal or action?
                - Categories: `create`, `read`, `update`, `delete`, `send`, `help`, `greeting`, `complaint`, `inquiry`, `campaign`.

                2. **MEANING** – Full actionable interpretation of what the user actually wants.

                3. **TONE** – Emotional tone of the message.
                - Options: `formal`, `casual`, `urgent`, `frustrated`, `happy`, `neutral`, `polite`.

                4. **ENTITIES** – Extract names, emails, phone numbers, dates, numbers, identifiers, or other structured information.

                5. **LANGUAGE** – Detect primary language (`ar`, `en`, `fr`).

                6. **DIALECT** – Detect dialect (Arabic: `Gulf`, `Maghrebi`, etc.; English: `American`, `British`; French: `Parisian`, etc.)

                7. **CONTEXT REFERENCES** – Identify any references to prior conversation context.

                8. **URGENCY** – Estimate urgency level (`low`, `normal`, `high`, `critical`).

                9. **CLARIFICATION** – Determine if additional information is needed to proceed.

                10. **RESPONSE TYPE** – `"simple"` or `"agent"` as before.
                    - `"simple"` → Use when ChatGPT can directly answer without requiring a specialist agent.  
                    - `"agent"` → Use when the query requires a specialist Siyadah AI agent.  

                11. **AGENT SELECTION** – If RESPONSE TYPE = agent, determine which Siyadah agents should be involved.

                - Possible agents:
                     - `content_agent` → كتابة المحتوى للحملات، الرسائل، واتساب، وإيميلات.
                     - `whatsApp_sender` → إرسال رسائل واتساب.
                     - `email_sender_agent` → إرسال الإيميلات.
                     - `db_agent` → إضافة، حذف، تعديل واستعلامات قواعد البيانات.

                - **Task Overlap Note:**
                    - `marketing_agent` and `sales_agent` can both prepare and send campaigns via WhatsApp or Email.
                    - Choose one or both depending on scope and purpose.
                        - `marketing_agent` → broad audiences, brand or product promotion.
                        - `sales_agent` → follow-up, targeted conversions, personalized offers.

                - You may include multiple agents when collaboration is required.
                    - Example: marketing creates a campaign → sales follows up → data_agent logs results.

                - Also specify **coordination_type**:
                    - `"sequential"` → one agent acts after another (e.g., marketing → sales).
                    - `"parallel"` → agents act simultaneously on related tasks.
                    - `"independent"` → each performs a distinct action.

                12. **CONFIDENCE** – Provide a confidence score between 0 and 1.

                ---

                ### Return only a JSON object:
                {{
                    "user_input": "the exact user input",
                    "intent": "main intent category",
                    "meaning": "detailed interpretation of user request",
                    "tone": "detected tone",
                    "entities": {{"key": "value"}},
                    "language": "ar/en/fr",
                    "dialect": "detected dialect or 'standard'",
                    "context_references": {{"pronoun": "reference"}},
                    "urgency": "low/normal/high/critical",
                    "needs_clarification": true/false,
                    "clarification_question": "question to ask if needed",
                    "response_type": "agent/simple",
                    "selected_agents": {["content_agent", "whatsApp_sender", "db_agent"]},
                    "coordination_type": "sequential/parallel/independent",
                    "confidence": 0.0–1.0
                }}
                """



    def _parse_json(self, content: str) -> dict:
        """Parse JSON from OpenAI response"""
        try:
            # Try direct parsing
            print("json.loads(content)      =================>", json.loads(content))
            return json.loads(content)
        except:
            # Try to extract JSON from text
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except:
                    pass
            
            # Return empty dict if parsing fails
            return {}


# Simple usage example
def main():
    """Test the understanding layer"""
    
    # Initialize
    layer = PromptUnderstandingLayer()
    
    # Test cases
    test_cases = [
        {
            "prompt": "أبغى أرسل حملة ايميلات ",
            "context": [
                {"role": "user", "content": "How many customers do I have?"},
                {"role": "assistant", "content": "You have 4 customers"},
                {"role": "user", "content": "Show me their names"},
                {"role": "assistant", "content": "The customers are: Ahmed, Sara, Mohammed, Fatima"}
            ]
        },
        {
            "prompt": "أضف عميل جديد",
            "context": []
        },
        {
            "prompt": "This is urgent! Fix it now!",
            "context": [
                {"role": "user", "content": "The email campaign isn't working"},
                {"role": "assistant", "content": "Let me check the campaign"}
            ]
        }
    ]
    
    print("=" * 60)
    print("TESTING PROMPT UNDERSTANDING LAYER")
    print("=" * 60)
    test_inputs = ["هلا والله و غلا  ",
                ]
    for i in test_inputs:

        
        # Understand the prompt
        understanding = layer.understand(
            user_prompt=i,
            context=[]
        )
        print("-----------------------------************----------------------------")
        print(understanding.to_dict())
        print("-----------------------------************----------------------------")


if __name__ == "__main__":
    main()
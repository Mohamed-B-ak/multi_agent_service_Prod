# Tools/intent_analysis_tools.py
import json
import re
from typing import Dict, List
from crewai.tools import BaseTool
import openai
import os

class IntentAnalysisTool(BaseTool):
    name: str = "Advanced Intent Analysis Tool"
    description: str = "Analyzes user input for complex, multi-layered intents with high precision"
    
    def _run(self, user_input: str, context: str = None) -> str:
        """
        تحليل النوايا المتقدم
        """
        try:
            # تحضير البيانات للتحليل
            analysis_prompt = f"""
            Analyze this user input for intent with extreme precision:
            
            User Input: "{user_input}"
            Context: {context if context else "No previous context"}
            
            Provide a detailed JSON analysis with:
            1. primary_intent: Main goal (send, create, analyze, manage, search, etc.)
            2. secondary_intent: Specific action (email, whatsapp, call, file, etc.)
            3. entities: {{
                "recipients": [list of people/emails],
                "topics": [list of subjects/topics],
                "timeframes": [any time references],
                "attachments": [any file references]
            }}
            4. modifiers: {{
                "urgency": "low/medium/high/urgent",
                "formality": "casual/professional/formal",
                "scope": "single/multiple/bulk",
                "privacy": "public/private/confidential"
            }}
            5. emotional_tone: "neutral/happy/concerned/frustrated/excited"
            6. complexity_score: 1-10 (how complex is this request)
            7. multi_step: true/false (does this require multiple actions)
            8. confidence_score: 0.0-1.0 (how confident in this analysis)
            
            Return ONLY valid JSON.
            """
            
            # استخدام OpenAI للتحليل المتقدم
            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert in intent analysis. Always return valid JSON."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            analysis_result = response.choices[0].message.content
            
            # التحقق من صحة JSON
            try:
                parsed_result = json.loads(analysis_result)
                return json.dumps(parsed_result, ensure_ascii=False, indent=2)
            except json.JSONDecodeError:
                # خطة بديلة إذا فشل التحليل
                return self._fallback_analysis(user_input)
                
        except Exception as e:
            return f"❌ Error in intent analysis: {str(e)}"
    
    def _fallback_analysis(self, user_input: str) -> str:
        """تحليل بديل بسيط"""
        fallback = {
            "primary_intent": "unknown",
            "secondary_intent": "unknown", 
            "entities": {"recipients": [], "topics": [], "timeframes": [], "attachments": []},
            "modifiers": {"urgency": "medium", "formality": "professional", "scope": "single", "privacy": "private"},
            "emotional_tone": "neutral",
            "complexity_score": 5,
            "multi_step": False,
            "confidence_score": 0.5,
            "note": "Fallback analysis - original analysis failed"
        }
        return json.dumps(fallback, ensure_ascii=False, indent=2)

class EmotionalToneDetector(BaseTool):
    name: str = "Emotional Tone Detector"
    description: str = "Detects emotional tone and communication style from text"
    
    def _run(self, text: str) -> str:
        """
        كشف النبرة العاطفية والأسلوب
        """
        # مؤشرات النبرة
        urgency_indicators = ["عاجل", "سريع", "فوراً", "urgent", "asap", "quickly", "immediately"]
        positive_indicators = ["شكراً", "ممتاز", "رائع", "thanks", "great", "excellent", "wonderful"]
        negative_indicators = ["مشكلة", "خطأ", "فشل", "problem", "error", "failed", "issue"]
        formal_indicators = ["حضرتك", "تفضلوا", "يرجى", "please", "kindly", "would you"]
        
        text_lower = text.lower()
        
        # تحديد النبرة
        tone_scores = {
            "urgency": sum(1 for indicator in urgency_indicators if indicator in text_lower),
            "positive": sum(1 for indicator in positive_indicators if indicator in text_lower),
            "negative": sum(1 for indicator in negative_indicators if indicator in text_lower),
            "formal": sum(1 for indicator in formal_indicators if indicator in text_lower)
        }
        
        # تحديد النبرة الغالبة
        dominant_tone = max(tone_scores, key=tone_scores.get) if max(tone_scores.values()) > 0 else "neutral"
        
        result = {
            "dominant_tone": dominant_tone,
            "tone_scores": tone_scores,
            "communication_style": "formal" if tone_scores["formal"] > 0 else "casual",
            "sentiment": "positive" if tone_scores["positive"] > tone_scores["negative"] else 
                        "negative" if tone_scores["negative"] > 0 else "neutral"
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)

class UrgencyAnalyzer(BaseTool):
    name: str = "Urgency Analyzer"
    description: str = "Analyzes urgency level and time-sensitive elements"
    
    def _run(self, text: str) -> str:
        """
        تحليل مستوى الإلحاح والوقت
        """
        urgency_keywords = {
            "urgent": ["عاجل", "فوري", "urgent", "asap", "immediately", "emergency"],
            "high": ["اليوم", "الآن", "سريع", "today", "now", "quickly", "soon"],
            "medium": ["غداً", "هذا الأسبوع", "tomorrow", "this week", "when possible"],
            "low": ["عندما تستطيع", "لا عجلة", "when you can", "no rush", "whenever"]
        }
        
        text_lower = text.lower()
        urgency_level = "medium"  # افتراضي
        
        for level, keywords in urgency_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                urgency_level = level
                break
        
        # تحليل المؤشرات الزمنية
        time_indicators = re.findall(r'\b(\d{1,2}:\d{2}|\d{1,2} (am|pm)|صباحاً|مساءً|morning|afternoon|evening)\b', text_lower)
        date_indicators = re.findall(r'\b(\d{1,2}/\d{1,2}|\d{1,2}-\d{1,2}|الاثنين|الثلاثاء|monday|tuesday|wednesday|thursday|friday)\b', text_lower)
        
        result = {
            "urgency_level": urgency_level,
            "has_time_constraint": len(time_indicators) > 0 or len(date_indicators) > 0,
            "time_indicators": time_indicators,
            "date_indicators": date_indicators,
            "estimated_priority": self._calculate_priority(urgency_level, time_indicators, date_indicators)
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
    
    def _calculate_priority(self, urgency: str, time_ind: list, date_ind: list) -> int:
        """حساب الأولوية من 1-10"""
        base_priority = {"urgent": 9, "high": 7, "medium": 5, "low": 3}
        priority = base_priority.get(urgency, 5)
        
        # زيادة الأولوية إذا كان هناك مؤشرات زمنية
        if time_ind:
            priority += 1
        if date_ind:
            priority += 1
            
        return min(priority, 10)
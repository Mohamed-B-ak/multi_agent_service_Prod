"""
simplified_intelligence_layer_final.py
النسخة النهائية المُصححة بالكامل
"""

import json
from openai import OpenAI
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
import os
import asyncio
import redis
from dotenv import load_dotenv

load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
MONGO_URI = os.getenv("MONGO_DB_URI", "mongodb://localhost:27017")


@dataclass
class IntelligenceResponse:
    """البنية الموحدة للرد"""
    intent: str
    sub_intents: List[str]
    confidence: float
    entities: Dict
    urgency: str
    user_context_summary: str
    relevant_history: List[Dict]
    user_preferences: Dict
    recommended_agent: str
    supporting_agents: List[str]
    execution_mode: str
    priority: str
    next_likely_action: str
    predictions: Dict
    recommendations: List[str]
    action_type: str
    direct_response: Optional[str]
    confirmation_question: Optional[str]
    semantic_rewrite: Optional[str]
    lang: Optional[str]
    processing_time: float
    method_used: str
    total_cost: float


class SimplifiedIntelligenceLayer:
    """
    طبقة ذكاء مبسطة تستخدم OpenAI لكل شيء
    """

    def __init__(self):
        # OpenAI Client
        self.client = OpenAI(api_key=OPENAI_API_KEY)

        # Storage connections
        self._init_storage()

        # Agent capabilities
        self.agent_capabilities = {
            "CustomerServiceAgent": {
                "skills": ["problem solving", "empathy", "escalation"],
                "tools": ["Database operations (CRUD)", "WhatsApp sender", "Email sender"],
                "intents": ["complaint", "help", "support"],
                "languages": ["ar", "en"],
            },
            "SalesAgent": {
                "skills": ["negotiation", "product knowledge", "closing deals"],
                "tools": ["Database operations (CRUD)", "WhatsApp sender", "Email sender"],
                "intents": ["purchase", "pricing", "quotes"],
                "languages": ["ar", "en"],
            },
            "TechnicalSupportAgent": {
                "skills": ["debugging", "technical guidance", "troubleshooting"],
                "tools": ["Database operations (CRUD)", "WhatsApp sender", "Email sender"],
                "intents": ["technical", "bug", "configuration"],
                "languages": ["ar", "en"],
            },
            "MarketingAgent": {
                "skills": ["campaign creation", "audience targeting", "analytics"],
                "tools": ["Database operations (CRUD)", "WhatsApp sender", "Email sender"],
                "intents": ["campaign", "promotion", "marketing"],
                "languages": ["ar", "en"],
            },
        }

        # In-memory fallback
        self.memory_storage = {
            "contexts": {},
            "conversations": []
        }

    def _init_storage(self):
        """تهيئة MongoDB (اختياري)"""
        try:
            from pymongo import MongoClient
            self.mongo_client = MongoClient(MONGO_URI)
            self.db = self.mongo_client["intelligence_db"]
        except Exception as e:
            print(f"⚠️ Mongo init failed: {e}")
            self.db = None

    async def process(
        self,
        user_input: str,
        user_email: str,
        redis_db,
        session_id: Optional[str] = None,
        use_gpt4: bool = False,
    ) -> IntelligenceResponse:
        """المعالج الرئيسي"""
        start_time = datetime.now()

        try:
            # 1. جلب السياق
            context = await self._fetch_context(user_email, redis_db, session_id)

            # 2. بناء البرومبت
            smart_prompt = self._build_smart_prompt(user_input, context)

            # 3. استدعاء OpenAI
            model = "gpt-4" if use_gpt4 else "gpt-3.5-turbo"

            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an intelligent assistant that analyzes user requests and returns structured JSON. You understand Arabic and English.",
                    },
                    {
                        "role": "user",
                        "content": smart_prompt,
                    },
                ],
                temperature=0.2,
                max_tokens=1500,
            )

            # 4. معالجة الرد
            content = response.choices[0].message.content
            result = self._parse_response(content)

            # 5. حساب التكلفة والوقت
            processing_time = (datetime.now() - start_time).total_seconds()
            cost = self._calculate_cost(model, dict(response.usage))

            # 6. بناء الرد
            intelligence_response = IntelligenceResponse(
                intent=result.get("intent", "unknown"),
                sub_intents=result.get("sub_intents", []),
                confidence=result.get("confidence", 0.0),
                entities=result.get("entities", {}),
                urgency=result.get("urgency", "normal"),
                user_context_summary=result.get("user_context_summary", ""),
                relevant_history=context.get("history", []),
                user_preferences=context.get("preferences", {}),
                recommended_agent=result.get("recommended_agent", "CustomerServiceAgent"),
                supporting_agents=result.get("supporting_agents", []),
                execution_mode=result.get("execution_mode", "single"),
                priority=result.get("priority", "normal"),
                next_likely_action=result.get("next_likely_action", ""),
                predictions=result.get("predictions", {}),
                recommendations=result.get("recommendations", []),
                action_type=result.get("action_type", "needs_agent"),
                direct_response=result.get("direct_response"),
                confirmation_question=result.get("confirmation_question"),
                semantic_rewrite=result.get("semantic_rewrite", ""),
                lang=result.get("lang", "en"),
                processing_time=processing_time,
                method_used=model,
                total_cost=cost,
            )

            # 7. حفظ التفاعل
            await self._save_interaction(user_email, user_input, intelligence_response)

            return intelligence_response

        except Exception as e:
            print(f"Error in processing: {e}")
            processing_time = (datetime.now() - start_time).total_seconds()
            return self._create_error_response(str(e), processing_time)

    def _parse_response(self, content: str) -> Dict:
        """معالجة الرد من OpenAI"""
        print("############################################################################")
        print(content)
        print("############################################################################")
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except:
                    pass
            return self._create_default_result()

    async def _fetch_context(self, user_email: str, redis_db, session_id: Optional[str]) -> Dict:
        """جلب السياق"""
        context = {
            "user_email": user_email,
            "history": [],
            "preferences": {"language": "ar", "communication_style": "formal"},
            "patterns": {}
        }

        try:
            if self.db is not None:
                conversations = list(
                    self.db.conversations.find(
                        {"user_email": user_email},
                        {"user_input": 1, "intent": 1, "timestamp": 1, "_id": 0}
                    ).sort("timestamp", -1).limit(5)
                )
                for conv in conversations:
                    if "timestamp" in conv and hasattr(conv["timestamp"], "isoformat"):
                        conv["timestamp"] = conv["timestamp"].isoformat()
                context["history"] = conversations

                profile = self.db.profiles.find_one({"email": user_email})
                if profile:
                    context["preferences"] = {
                        "language": profile.get("language_preference", "ar"),
                        "communication_style": profile.get("communication_style", "formal")
                    }
            else:
                if user_email in self.memory_storage["contexts"]:
                    context = self.memory_storage["contexts"][user_email]
        except Exception as e:
            print(f"⚠️ Context fetch warning: {e}")

        return context

    async def _save_interaction(self, user_email: str, user_input: str, response: IntelligenceResponse):
        """حفظ التفاعل"""
        interaction = {
            "user_email": user_email,
            "timestamp": datetime.now(),
            "user_input": user_input,
            "intent": response.intent,
            "confidence": response.confidence,
            "agent_used": response.recommended_agent,
            "processing_time": response.processing_time,
            "method": response.method_used,
            "cost": response.total_cost
        }

        try:
            if self.db is not None:
                self.db.conversations.insert_one(interaction.copy())
            else:
                self.memory_storage["conversations"].append(interaction)

                if user_email not in self.memory_storage["contexts"]:
                    self.memory_storage["contexts"][user_email] = {
                        "history": [],
                        "preferences": {},
                        "patterns": {}
                    }

                self.memory_storage["contexts"][user_email]["history"].append({
                    "user_input": user_input,
                    "intent": response.intent,
                    "timestamp": interaction["timestamp"].isoformat()
                })

                if len(self.memory_storage["contexts"][user_email]["history"]) > 5:
                    self.memory_storage["contexts"][user_email]["history"] = \
                        self.memory_storage["contexts"][user_email]["history"][-5:]
        except Exception as e:
            print(f"⚠️ Save warning: {e}")

    def _build_smart_prompt(self, user_input: str, context: Dict) -> str:
        """بناء برومبت ذكي"""
        agents_info = json.dumps(self.agent_capabilities, indent=2)
        context_str = json.dumps(context, ensure_ascii=False, indent=2)
        
        return  f"""
Analyze this user request and return ONLY JSON.

USER INPUT: "{user_input}"
CONTEXT: {context_str}
AGENTS: {agents_info}

RULES:

[Intent Detection]
- Identify the **primary intent** semantically (not keyword-based).
- Allowed values: ["greeting", "express_gratitude", "add_client", 
  "report_problem", "pricing_inquiry", "marketing_campaign", 
  "query_info", "other"].
- Detect sub-intents if present and return as an array.
- If confidence < 0.5, fallback to "other".

[Entities Extraction]
- Extract structured data (e.g., customer names, product names, dates, locations).
- Always return in form: [{{"type": "entity_type", "value": "entity_value"}}].
- If required or mandatory entities are missing OR the request is vague/underspecified 
  (even after considering CONTEXT), force action_type = "needs_confirmation".

[Urgency Classification]
- Classify request as: "low", "normal", or "urgent".

[Contextual Understanding]
- Briefly summarize relevant context/history.

[Agent Recommendation]
- Map intents to agents only when required:
    • greeting → null  
    • express_gratitude → null  
    • add_client → DatabaseAgent  
    • report_problem → CustomerServiceAgent  
    • pricing_inquiry → SalesAgent  
    • marketing_campaign → MarketingAgent  
    • query_info → null (unless product/pricing → SalesAgent)  
    • other → null
- If multiple agents might help, include them in "supporting_agents".

[Action Handling]
- action_type options:
    • "direct_response" → can answer immediately without agent and no clarification needed.  
    • "needs_agent" → requires agent AND all required entities are fully provided.  
    • "needs_confirmation" → request is unclear, vague, or missing details. Always ask a direct clarifying question before proceeding.  
- Always set "need_more_data" = true when information is incomplete.  
- If action_type = "needs_confirmation", "confirmation_question" must contain a natural, direct clarifying question in the user’s language.  
- Never assume unspecified details. Always confirm with the user first.  
- Never allow "needs_agent" if entities are missing or unclear.  
- This rule applies to **all intents**, not only add_client or marketing_campaign.

[Specialist Agent Prompt Construction]
- If action_type = "needs_agent", build an "agent_prompt" string that is:
    • Self-contained and unambiguous.  
    • Includes: USER INPUT, CONTEXT summary, extracted ENTITIES, identified INTENT, and clarified goals.  
    • Written as clear instructions for the recommended agent.  
    • Example:  
        "The user wants to add a new client. Context: previous interactions suggest they are onboarding. Entities: {{'client_name': 'Acme Corp'}}. Task: Register this client in the database and confirm success."  
- agent_prompt must be null if action_type ≠ "needs_agent".

[Direct Response Rules]
- If intent = "express_gratitude":
    • Respond politely in Arabic, with formal but warm tone.
- If intent = "greeting":
    • Respond with a polite Arabic greeting acknowledging the user.
- If intent = "other" but conversational:
    • Provide a short, polite, informative direct response.
- If action_type = "needs_confirmation":
    • Do not generate "direct_response". Instead populate only "confirmation_question".
- In all direct responses:
    • recommended_agent = null
    • supporting_agents = []
    • direct_response must never be null unless action_type = "needs_confirmation".

[Semantic Expansion]
- Rewrite user request into a clear, detailed, contextualized form.
- Resolve vague pronouns using context when possible.
- Add this as "semantic_rewrite" in output.
- If underspecified, highlight the ambiguity explicitly.

[Predictions & Recommendations]
- Predict likely next action.
- Suggest helpful recommendations.

FINAL JSON OUTPUT SCHEMA:
{{
    "intent": "primary_intent",
    "sub_intents": [],
    "confidence": 0.0-1.0,
    "entities": [],
    "urgency": "normal",
    "user_context_summary": "summary",
    "recommended_agent": "AgentName or null",
    "supporting_agents": [],
    "execution_mode": "single",
    "priority": "normal",
    "next_likely_action": "next_action",
    "predictions": {{}},
    "recommendations": [],
    "action_type": "direct_response/needs_agent/needs_confirmation",
    "direct_response": null or "response",
    "confirmation_question": null or "question",
    "semantic_rewrite": "expanded and clarified version of the user request",
    "agent_prompt": null or "specialist-ready instruction string",
    "lang" : the user input language ar/en/fr , default "en"
    "need_more_data": false
}}
"""


    def _calculate_cost(self, model: str, usage: Dict) -> float:
        """حساب التكلفة"""
        costs = {
            "gpt-3.5-turbo": {"prompt": 0.001, "completion": 0.002},
            "gpt-4": {"prompt": 0.03, "completion": 0.06},
        }

        model_costs = costs.get(model, costs["gpt-3.5-turbo"])
        prompt_tokens = usage.get("prompt_tokens", 0) / 1000
        completion_tokens = usage.get("completion_tokens", 0) / 1000

        total = (prompt_tokens * model_costs["prompt"]) + (completion_tokens * model_costs["completion"])
        return round(total, 6)

    def _create_default_result(self) -> Dict:
        """نتيجة افتراضية"""
        return {
            "intent": "unknown",
            "sub_intents": [],
            "confidence": 0.5,
            "entities": {},
            "urgency": "normal",
            "user_context_summary": "Processing",
            "recommended_agent": "CustomerServiceAgent",
            "supporting_agents": [],
            "execution_mode": "single",
            "priority": "normal",
            "next_likely_action": "",
            "predictions": {},
            "recommendations": [],
            "action_type": "needs_confirmation",
            "direct_response": None,
            "confirmation_question": "كيف يمكنني مساعدتك؟",
        }

    def _create_error_response(self, error: str, processing_time: float) -> IntelligenceResponse:
        """رد الخطأ"""
        return IntelligenceResponse(
            intent="error",
            sub_intents=["system_error"],
            confidence=0.0,
            entities={},
            urgency="normal",
            user_context_summary=f"Error: {error[:100]}",
            relevant_history=[],
            user_preferences={},
            recommended_agent="CustomerServiceAgent",
            supporting_agents=[],
            execution_mode="single",
            priority="high",
            next_likely_action="retry",
            predictions={},
            recommendations=["Please try again"],
            action_type="direct_response",
            direct_response="عذراً، حدث خطأ. يرجى المحاولة مرة أخرى.",
            confirmation_question=None,
            processing_time=processing_time,
            method_used="error",
            lang="en",
            total_cost=0.0,
        )


# ============== MAIN TEST ==============

async def main(user_email, user_input, redis_db):
    """اختبار الطبقة الذكية"""
    intelligence = SimplifiedIntelligenceLayer()
    try:
        return await intelligence.process(user_input, user_email, redis_db, use_gpt4=False)
    except Exception as e:
        print(f"❌ Error: {e}")
        return "An error occurred when we tried to execute the user input"


if __name__ == "__main__":
    import asyncio
    import redis

    # بريد المستخدم (ثابت للتجربة)
    user_email = "tester@example.com"

    # قائمة الطلبات للتجربة (20 مثال متنوع)
    test_inputs = [
        "السلام عليكم",  # تحية
        "شكرًا جزيلًا على مساعدتك",  # شكر
        "أريد معرفة سعر المنتج X",  # استعلام سعر
        "أريد شراء 5 قطع من المنتج Y",  # طلب شراء
        "لدي مشكلة في تسجيل الدخول",  # شكوى تقنية
        "أريد إطلاق حملة تسويقية جديدة لمنتج Z",  # تسويق
        "أضف عميل جديد اسمه أحمد برقم 0501234567",  # إضافة عميل
        "ممكن تفاصيل أكثر عن الباقة الذهبية؟",  # استعلام معلومات
        "يوجد خطأ في فاتورتي الأخيرة",  # شكوى
        "أحتاج عرض سعر لكمية 100 وحدة",  # مبيعات
        "أريد إرسال بريد تسويقي لعملاء جدة",  # تسويق
        "المنتج لا يعمل عندي",  # دعم فني
        "أريد تحديث بياناتي",  # تعديل بيانات
        "أعطني تفاصيل عن آخر عميل أضفته",  # استعلام تاريخ
        "ممكن تنصحني بالخطة الأفضل لشركتي الصغيرة؟",  # توصية
        "هل ممكن التواصل عبر واتساب بدل الإيميل؟",  # تفضيل تواصل
        "عميل اسمه فهد بريد fhd@example.com رقم 0556784321",  # إضافة عميل جديد
        "ممكن تعمل خصم على الطلب الكبير؟",  # تفاوض/مبيعات
        "أريد إعداد حملة إعلانية على فيسبوك",  # تسويق
        "شكراً لكم، كانت التجربة ممتازة",  # شكر
    ]

    # Redis client (محلي أو من env)
    redis_client = redis.from_url(
        os.getenv("REDIS_URL", "redis://localhost:6379"),
        decode_responses=True,
    )

    async def run_tests():
        for i, user_prompt in enumerate(test_inputs, start=1):
            print(f"\n====== الطلب رقم {i}: {user_prompt} ======")
            result = await main(user_email, user_prompt, redis_client)
            print("************************************")
            print(result)

    asyncio.run(run_tests())

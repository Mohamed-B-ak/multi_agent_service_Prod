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
    processing_time: float
    method_used: str
    total_cost: float
    semantic_rewrite: Optional[str] = None
    lang: Optional[str] = "en"


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
        
        return f"""
                قم بتحليل مدخل المستخدم بدقة وأرجع فقط JSON صالح وفقًا للمخطط المحدد أدناه.

                INPUT: "{user_input}"
                CONTEXT: {context_str}
                AGENTS: {agents_info}

                القواعد:

                1. يجب أن تكون الاستجابة دائمًا بنفس لغة أو لهجة المستخدم (لا تغيّر اللغة).  
                2. تأكد أن النتيجة مرتبطة بالسياق المستلم من واجهة المحادثة.  
                3. إذا كان طلب المستخدم مباشرًا وبسيطًا ولا يتطلب تدخل وكيل (بحسب قدرات {agents_info})، ضع الإجابة في الحقل direct_response داخل JSON.  
                4. إذا كان طلب المستخدم غامضًا أو غير مكتمل، اطلب توضيحًا إضافيًا منه وضع السؤال في الحقل confirmation_question داخل JSON.  
                5. التزم بالمخطط المعطى حرفيًا: لا تضف أو تحذف مفاتيح، حتى لو كانت فارغة.  
                6. قيمة الحقل "lang" يجب أن تعكس لغة المستخدم تلقائيًا (مثال: "ar" إذا كانت بالعربية، "en" إذا بالإنجليزية).  
                7. لا تُرجع أي نص أو تفسير خارج JSON.  

                OUTPUT JSON SCHEMA:
                {{
                "intent": "",
                "sub_intents": [],
                "confidence": 0.0,
                "entities": [],
                "urgency": "normal",
                "user_context_summary": "",
                "recommended_agent": null,
                "supporting_agents": [],
                "execution_mode": "single",
                "priority": "normal",
                "next_likely_action": "",
                "predictions": {{}},
                "recommendations": [],
                "action_type": "",
                "direct_response": null,
                "confirmation_question": null,
                "semantic_rewrite": "",
                "agent_prompt": null,
                "lang": "",
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
"أريد إضافة عميل جديد للنظام.",

"سجّل عميل جديد اسمه أحمد علي.",

"أضف العميل محمد حسن إلى قاعدة البيانات.",

"أريد تسجيل بيانات عميل جديد.",

"كيف يمكنني إضافة عميل جديد؟",

"أدخل عميل جديد برقم هاتف 0501234567.",

"أريد إنشاء حساب لعميل جديد.",

"أضف هذا العميل: الاسم خالد، البريد khaled@test.com",

"سجّل عميل جديد عندنا.",

"هل يمكنك إضافة عميل جديد للنظام؟",

"أدخل بيانات عميل جديد للشركة.",

"أريد إضافة زبون جديد الآن.",

"سجّل عميل جديد اسمه سارة محمد.",

"أضف عميل جديد مع البريد الإلكتروني sara@test.com.",

"كيف أضيف عميل جديد لقاعدة العملاء؟",

"أريد إضافة عميل باسم شركة المستقبل.",

"رجاءً أضف عميل جديد برقم 12345.",

"أدخل عميل جديد في النظام الإداري.",

"سجّل عميل جديد مع التفاصيل التالية: الاسم: أحمد، الهاتف: 0555555555.",

"أريد إنشاء سجل جديد لعميل في النظام.",
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
            #print(result)
            print("##########################################")
            print("##########################################")
            if result.confirmation_question:
                print("Needs confirmation:", result.confirmation_question)

            elif result.direct_response:
                print("Direct response:", result.direct_response)
            print("##########################################")
            print("##########################################")

    asyncio.run(run_tests())

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
    semantic_rewrite: Optional[str] = None
    lang: Optional[str] = "en"


class SimplifiedIntelligenceLayer:
    """
    طبقة ذكاء مبسطة تستخدم OpenAI لكل شيء
    """

    def __init__(self):
        # OpenAI Client
        self.client = OpenAI(api_key=OPENAI_API_KEY)

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



    async def process(
        self,
        user_input: str,
        user_email: str,
        redis_db,
        context,
        session_id: Optional[str] = None,
        use_gpt4: bool = False,
    ) -> IntelligenceResponse:
        """المعالج الرئيسي"""
        start_time = datetime.now()

        try:
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
            print("//////////////////////////////////////////////////////////////////////")
            print(content)
            print("//////////////////////////////////////////////////////////////////////")
            result = self._parse_response(content)

            # 5. حساب التكلفة والوقت
            processing_time = (datetime.now() - start_time).total_seconds()


            # 6. بناء الرد
            intelligence_response = IntelligenceResponse(
                intent=result.get("intent", "unknown"),
                sub_intents=result.get("sub_intents", []),
                confidence=result.get("confidence", 0.0),
                entities=result.get("entities", {}),
                urgency=result.get("urgency", "normal"),
                user_context_summary=result.get("user_context_summary", ""),
                relevant_history="None",
                user_preferences="None",
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
            )
            
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
        )


# ============== MAIN TEST ==============

async def main(user_email, user_input, redis_db, context):
    """اختبار الطبقة الذكية"""
    intelligence = SimplifiedIntelligenceLayer()
    try:
        return await intelligence.process(user_input, user_email, redis_db, context, use_gpt4=False)
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
    context = []
    async def run_tests():
        for i, user_prompt in enumerate(test_inputs, start=1):
            print(f"\n====== الطلب رقم {i}: {user_prompt} ======")
            result = await main(user_email, user_prompt, redis_client, context)
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

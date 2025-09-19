# Tools/context_memory_tools.py
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from crewai.tools import BaseTool
from pymongo import MongoClient
import os

class ConversationMemoryTool(BaseTool):
    name: str = "Conversation Memory Tool"
    description: str = "Stores and retrieves conversation history and context"
    
    user_email: str
    
    def __init__(self, user_email: str, **kwargs):
        super().__init__(**kwargs)
        self.user_email = user_email
        self.client = MongoClient(os.getenv("MONGO_DB_URI"))
        self.db = self.client[os.getenv("DB_NAME")]
        self.collection = self.db["conversation_memory"]
        
        # إنشاء فهرس للبحث السريع
        try:
            self.collection.create_index([("user_email", 1), ("timestamp", -1)])
            self.collection.create_index([("user_email", 1), ("tags", 1)])
        except:
            pass  # الفهرس موجود بالفعل
    
    def _run(self, action: str, data: Optional[Dict] = None, query: Optional[str] = None) -> str:
        """
        إدارة ذاكرة المحادثات
        """
        try:
            if action == "store":
                return self._store_conversation(data)
            elif action == "retrieve":
                return self._retrieve_conversations(query)
            elif action == "analyze":
                return self._analyze_conversation_patterns()
            else:
                return f"❌ Invalid action: {action}. Use: store, retrieve, analyze"
        except Exception as e:
            return f"❌ Memory error: {str(e)}"
    
    def _store_conversation(self, data: Dict) -> str:
        """تخزين محادثة جديدة"""
        if not data:
            return "❌ No data provided to store"
            
        conversation_record = {
            "user_email": self.user_email,
            "timestamp": datetime.utcnow(),
            "user_input": data.get("user_input", ""),
            "intent_analysis": data.get("intent_analysis", {}),
            "system_response": data.get("system_response", ""),
            "success": data.get("success", True),
            "context": data.get("context", {}),
            "tags": self._extract_tags(data.get("user_input", "")),
            "importance_score": self._calculate_importance(data)
        }
        
        result = self.collection.insert_one(conversation_record)
        return f"✅ Conversation stored with ID: {result.inserted_id}"
    
    def _retrieve_conversations(self, query: str, limit: int = 10) -> str:
        """استرجاع المحادثات ذات الصلة"""
        if not query:
            # إذا لم يكن هناك query، أحضر أحدث المحادثات
            conversations = list(self.collection.find(
                {"user_email": self.user_email},
                {"_id": 0, "user_input": 1, "system_response": 1, "timestamp": 1, "context": 1, "tags": 1}
            ).sort("timestamp", -1).limit(limit))
        else:
            # البحث في النص والعلامات
            search_filter = {
                "user_email": self.user_email,
                "$or": [
                    {"user_input": {"$regex": query, "$options": "i"}},
                    {"system_response": {"$regex": query, "$options": "i"}},
                    {"tags": {"$in": [query.lower()]}}
                ]
            }
            
            conversations = list(self.collection.find(
                search_filter,
                {"_id": 0, "user_input": 1, "system_response": 1, "timestamp": 1, "context": 1, "tags": 1}
            ).sort("timestamp", -1).limit(limit))
        
        if not conversations:
            return json.dumps({
                "message": "No relevant conversations found",
                "total_found": 0
            }, ensure_ascii=False)
        
        return json.dumps({
            "relevant_conversations": conversations,
            "total_found": len(conversations)
        }, default=str, ensure_ascii=False, indent=2)
    
    def _analyze_conversation_patterns(self) -> str:
        """تحليل أنماط المحادثة"""
        # آخر 30 يوم
        since_date = datetime.utcnow() - timedelta(days=30)
        
        try:
            # تحليل العلامات الأكثر استخداماً
            pipeline = [
                {"$match": {"user_email": self.user_email, "timestamp": {"$gte": since_date}}},
                {"$unwind": "$tags"},
                {"$group": {
                    "_id": "$tags",
                    "count": {"$sum": 1},
                    "avg_importance": {"$avg": "$importance_score"}
                }},
                {"$sort": {"count": -1}},
                {"$limit": 10}
            ]
            
            patterns = list(self.collection.aggregate(pipeline))
            
            # إحصائيات عامة
            total_conversations = self.collection.count_documents({
                "user_email": self.user_email, 
                "timestamp": {"$gte": since_date}
            })
            
            successful_conversations = self.collection.count_documents({
                "user_email": self.user_email,
                "timestamp": {"$gte": since_date},
                "success": True
            })
            
            success_rate = (successful_conversations / total_conversations * 100) if total_conversations > 0 else 0
            
            return json.dumps({
                "conversation_patterns": patterns,
                "analysis_period": "last_30_days",
                "total_conversations": total_conversations,
                "success_rate": round(success_rate, 2),
                "most_common_topics": [p["_id"] for p in patterns[:5]]
            }, default=str, ensure_ascii=False, indent=2)
            
        except Exception as e:
            return f"❌ Pattern analysis error: {str(e)}"
    
    def _extract_tags(self, text: str) -> List[str]:
        """استخراج علامات من النص"""
        if not text:
            return []
            
        tags = []
        text_lower = text.lower()
        
        # علامات الموضوعات
        if any(word in text_lower for word in ["email", "إيميل", "بريد"]):
            tags.append("email")
        if any(word in text_lower for word in ["whatsapp", "واتساب", "رسالة"]):
            tags.append("whatsapp")
        if any(word in text_lower for word in ["call", "مكالمة", "اتصال"]):
            tags.append("call")
        if any(word in text_lower for word in ["database", "قاعدة", "بيانات", "data"]):
            tags.append("database")
        if any(word in text_lower for word in ["file", "ملف", "pdf", "word", "excel"]):
            tags.append("file")
        if any(word in text_lower for word in ["help", "مساعدة", "support", "دعم"]):
            tags.append("support")
        
        return tags
    
    def _calculate_importance(self, data: Dict) -> float:
        """حساب أهمية المحادثة"""
        if not data:
            return 5.0
            
        score = 5.0  # نقطة البداية
        
        # زيادة النتيجة بناءً على عوامل مختلفة
        user_input = data.get("user_input", "").lower()
        
        if any(word in user_input for word in ["urgent", "عاجل", "important", "مهم"]):
            score += 2.0
        
        if data.get("success", True):
            score += 1.0
        else:
            score += 2.0  # الأخطاء مهمة للتعلم
        
        # طول النص يدل على التعقيد
        if len(user_input) > 100:
            score += 1.0
        
        return min(score, 10.0)

class UserPatternAnalyzer(BaseTool):
    name: str = "User Pattern Analyzer"
    description: str = "Analyzes user behavior patterns and preferences"
    
    user_email: str
    
    def __init__(self, user_email: str, **kwargs):
        super().__init__(**kwargs)
        self.user_email = user_email
        self.client = MongoClient(os.getenv("MONGO_DB_URI"))
        self.db = self.client[os.getenv("DB_NAME")]
        self.collection = self.db["conversation_memory"]
    
    def _run(self, analysis_type: str = "comprehensive") -> str:
        """
        تحليل أنماط المستخدم
        """
        try:
            if analysis_type == "comprehensive":
                return self._comprehensive_analysis()
            elif analysis_type == "preferences":
                return self._analyze_preferences()
            elif analysis_type == "timing":
                return self._analyze_timing_patterns()
            else:
                return self._comprehensive_analysis()
        except Exception as e:
            return f"❌ Pattern analysis error: {str(e)}"
    
    def _comprehensive_analysis(self) -> str:
        """تحليل شامل للأنماط"""
        # تحليل آخر 60 يوم
        since_date = datetime.utcnow() - timedelta(days=60)
        
        conversations = list(self.collection.find({
            "user_email": self.user_email,
            "timestamp": {"$gte": since_date}
        }).sort("timestamp", -1))
        
        if not conversations:
            return json.dumps({
                "message": "No conversation history found for analysis",
                "user_email": self.user_email
            }, ensure_ascii=False)
        
        # تحليل الأنماط
        patterns = {
            "total_conversations": len(conversations),
            "most_common_intents": self._analyze_intents(conversations),
            "communication_style": self._analyze_communication_style(conversations),
            "preferred_channels": self._analyze_preferred_channels(conversations),
            "activity_patterns": self._analyze_activity_patterns(conversations),
            "success_rate": self._calculate_success_rate(conversations)
        }
        
        return json.dumps(patterns, default=str, ensure_ascii=False, indent=2)
    
    def _analyze_intents(self, conversations: List[Dict]) -> Dict:
        """تحليل النوايا الأكثر استخداماً"""
        intent_counts = {}
        for conv in conversations:
            tags = conv.get("tags", [])
            for tag in tags:
                intent_counts[tag] = intent_counts.get(tag, 0) + 1
        
        # ترتيب النوايا حسب الاستخدام
        if intent_counts:
            sorted_intents = sorted(intent_counts.items(), key=lambda x: x[1], reverse=True)
            return dict(sorted_intents[:5])  # أهم 5 نوايا
        
        return {"no_clear_patterns": True}
    
    def _analyze_communication_style(self, conversations: List[Dict]) -> Dict:
        """تحليل أسلوب التواصل"""
        formal_indicators = 0
        urgent_indicators = 0
        total_messages = len(conversations)
        
        for conv in conversations:
            user_input = conv.get("user_input", "").lower()
            
            if any(word in user_input for word in ["please", "يرجى", "تفضل", "kindly", "حضرتك"]):
                formal_indicators += 1
            
            if any(word in user_input for word in ["urgent", "عاجل", "quickly", "سريع", "فوري"]):
                urgent_indicators += 1
        
        return {
            "formality_score": round(formal_indicators / total_messages, 2) if total_messages > 0 else 0,
            "urgency_tendency": round(urgent_indicators / total_messages, 2) if total_messages > 0 else 0,
            "communication_style": "formal" if formal_indicators > total_messages * 0.3 else "casual",
            "total_analyzed": total_messages
        }
    
    def _analyze_preferred_channels(self, conversations: List[Dict]) -> Dict:
        """تحليل القنوات المفضلة"""
        channel_usage = {}
        for conv in conversations:
            tags = conv.get("tags", [])
            for tag in ["email", "whatsapp", "call", "database", "file"]:
                if tag in tags:
                    channel_usage[tag] = channel_usage.get(tag, 0) + 1
        
        total = sum(channel_usage.values())
        if total == 0:
            return {"no_clear_preference": True}
        
        # تحويل إلى نسب مئوية
        preferences = {channel: round((count/total)*100, 1) for channel, count in channel_usage.items()}
        
        # ترتيب حسب التفضيل
        sorted_preferences = dict(sorted(preferences.items(), key=lambda x: x[1], reverse=True))
        
        return {
            "preferences_percentage": sorted_preferences,
            "most_used_channel": max(channel_usage, key=channel_usage.get) if channel_usage else None,
            "total_interactions": total
        }
    
    def _analyze_activity_patterns(self, conversations: List[Dict]) -> Dict:
        """تحليل أنماط النشاط الزمني"""
        hours = {}
        days = {}
        
        for conv in conversations:
            timestamp = conv.get("timestamp")
            if timestamp and isinstance(timestamp, datetime):
                hour = timestamp.hour
                day = timestamp.strftime("%A")
                
                hours[hour] = hours.get(hour, 0) + 1
                days[day] = days.get(day, 0) + 1
        
        # أكثر الساعات والأيام نشاطاً
        most_active_hour = max(hours.items(), key=lambda x: x[1])[0] if hours else None
        most_active_day = max(days.items(), key=lambda x: x[1])[0] if days else None
        
        return {
            "most_active_hour": most_active_hour,
            "most_active_day": most_active_day,
            "hourly_distribution": hours,
            "daily_distribution": days,
            "peak_activity_times": self._get_peak_times(hours)
        }
    
    def _get_peak_times(self, hours: Dict) -> List[str]:
        """تحديد أوقات الذروة"""
        if not hours:
            return []
        
        avg_activity = sum(hours.values()) / len(hours)
        peak_hours = [hour for hour, count in hours.items() if count > avg_activity * 1.5]
        
        # تحويل إلى فترات زمنية مفهومة
        peak_periods = []
        for hour in sorted(peak_hours):
            if 6 <= hour < 12:
                period = "morning"
            elif 12 <= hour < 18:
                period = "afternoon"
            elif 18 <= hour < 22:
                period = "evening"
            else:
                period = "night"
            
            if period not in peak_periods:
                peak_periods.append(period)
        
        return peak_periods
    
    def _calculate_success_rate(self, conversations: List[Dict]) -> float:
        """حساب معدل النجاح"""
        successful = sum(1 for conv in conversations if conv.get("success", True))
        total = len(conversations)
        return round((successful / total * 100), 1) if total > 0 else 100.0

class ContextRetrievalTool(BaseTool):
    name: str = "Context Retrieval Tool"
    description: str = "Retrieves relevant context for current user requests"
    
    user_email: str
    
    def __init__(self, user_email: str, **kwargs):
        super().__init__(**kwargs)
        self.user_email = user_email
        self.client = MongoClient(os.getenv("MONGO_DB_URI"))
        self.db = self.client[os.getenv("DB_NAME")]
        self.collection = self.db["conversation_memory"]
    
    def _run(self, current_request: str, context_type: str = "relevant") -> str:
        """
        استرجاع السياق ذي الصلة
        """
        try:
            if context_type == "recent":
                return self._get_recent_context()
            elif context_type == "similar":
                return self._get_similar_context(current_request)
            elif context_type == "relevant":
                return self._get_relevant_context(current_request)
            else:
                return self._get_relevant_context(current_request)
        except Exception as e:
            return f"❌ Context retrieval error: {str(e)}"
    
    def _get_recent_context(self, limit: int = 5) -> str:
        """السياق الحديث"""
        recent_conversations = list(self.collection.find(
            {"user_email": self.user_email},
            {"user_input": 1, "system_response": 1, "timestamp": 1, "tags": 1, "_id": 0}
        ).sort("timestamp", -1).limit(limit))
        
        return json.dumps({
            "recent_context": recent_conversations,
            "context_type": "recent_conversations",
            "count": len(recent_conversations)
        }, default=str, ensure_ascii=False, indent=2)
    
    def _get_similar_context(self, current_request: str) -> str:
        """السياق المشابه"""
        # استخدام البحث النصي والعلامات للعثور على محادثات مشابهة
        search_terms = current_request.lower().split()[:5]  # أهم 5 كلمات
        
        similar_conversations = []
        
        # البحث بالعلامات أولاً
        for term in search_terms:
            conversations = list(self.collection.find({
                "user_email": self.user_email,
                "tags": {"$in": [term]}
            }, {
                "user_input": 1, "system_response": 1, "timestamp": 1, 
                "tags": 1, "importance_score": 1, "_id": 0
            }).sort("importance_score", -1).limit(2))
            
            similar_conversations.extend(conversations)
        
        # إزالة التكرارات
        seen = set()
        unique_conversations = []
        for conv in similar_conversations:
            conv_id = conv.get("user_input", "")
            if conv_id not in seen:
                seen.add(conv_id)
                unique_conversations.append(conv)
        
        return json.dumps({
            "similar_context": unique_conversations[:3],  # أهم 3
            "context_type": "similar_requests",
            "search_terms_used": search_terms
        }, default=str, ensure_ascii=False, indent=2)
    
    def _get_relevant_context(self, current_request: str) -> str:
        """السياق ذو الصلة (مزيج من الحديث والمشابه)"""
        # الحصول على السياق الحديث والمشابه
        recent_data = json.loads(self._get_recent_context(3))
        similar_data = json.loads(self._get_similar_context(current_request))
        
        return json.dumps({
            "comprehensive_context": {
                "recent_conversations": recent_data["recent_context"],
                "similar_conversations": similar_data["similar_context"],
                "context_summary": self._generate_context_summary(recent_data["recent_context"], similar_data["similar_context"])
            },
            "context_type": "comprehensive"
        }, default=str, ensure_ascii=False, indent=2)
    
    def _generate_context_summary(self, recent: List[Dict], similar: List[Dict]) -> Dict:
        """إنتاج ملخص للسياق"""
        all_conversations = recent + similar
        
        if not all_conversations:
            return {"message": "No context available"}
        
        # استخراج الأنماط الشائعة
        all_tags = []
        for conv in all_conversations:
            all_tags.extend(conv.get("tags", []))
        
        # أكثر المواضيع تكراراً
        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        common_topics = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            "total_conversations_analyzed": len(all_conversations),
            "most_common_topics": [topic[0] for topic in common_topics],
            "conversation_timeline": f"From {len(recent)} recent + {len(similar)} similar conversations",
            "key_insights": self._extract_key_insights(all_conversations)
        }
    
    def _extract_key_insights(self, conversations: List[Dict]) -> List[str]:
        """استخراج الأفكار الرئيسية"""
        insights = []
        
        if len(conversations) >= 3:
            insights.append(f"User has {len(conversations)} related interactions")
        
        # تحليل التكرار
        topics = {}
        for conv in conversations:
            for tag in conv.get("tags", []):
                topics[tag] = topics.get(tag, 0) + 1
        
        if topics:
            most_frequent = max(topics, key=topics.get)
            insights.append(f"Most frequent topic: {most_frequent}")
        
        # تحليل الوقت
        timestamps = [conv.get("timestamp") for conv in conversations if conv.get("timestamp")]
        if len(timestamps) > 1:
            latest = max(timestamps)
            earliest = min(timestamps)
            if isinstance(latest, datetime) and isinstance(earliest, datetime):
                days_span = (latest - earliest).days
                insights.append(f"Conversations span {days_span} days")
        
        return insights[:3]  # أهم 3 أفكار
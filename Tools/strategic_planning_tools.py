# Tools/strategic_planning_tools.py
import json
from typing import Dict, List
from crewai.tools import BaseTool

class ExecutionPlannerTool(BaseTool):
    name: str = "Execution Planner Tool"
    description: str = "Creates detailed execution plans for complex tasks"
    
    def _run(self, intent_analysis: str, context_data: str = "", user_requirements: str = "") -> str:
        """
        إنشاء خطة تنفيذ مفصلة
        """
        try:
            # تحليل البيانات المدخلة
            if isinstance(intent_analysis, str):
                try:
                    intent_data = json.loads(intent_analysis)
                except:
                    intent_data = {"primary_intent": "unknown", "complexity_score": 5}
            else:
                intent_data = intent_analysis
            
            # تحديد استراتيجية التنفيذ
            execution_strategy = self._determine_execution_strategy(intent_data)
            
            # تخطيط خطوات التنفيذ
            execution_steps = self._plan_execution_steps(intent_data, execution_strategy)
            
            # تحديد الموارد المطلوبة
            required_resources = self._identify_required_resources(intent_data, execution_steps)
            
            # تقدير الوقت
            time_estimation = self._estimate_execution_time(execution_steps)
            
            execution_plan = {
                "execution_strategy": execution_strategy,
                "execution_steps": execution_steps,
                "required_resources": required_resources,
                "time_estimation": time_estimation,
                "success_criteria": self._define_success_criteria(intent_data),
                "quality_checkpoints": self._define_quality_checkpoints(execution_steps)
            }
            
            return json.dumps(execution_plan, ensure_ascii=False, indent=2)
            
        except Exception as e:
            return f"❌ Execution planning error: {str(e)}"
    
    def _determine_execution_strategy(self, intent_data: Dict) -> Dict:
        """تحديد استراتيجية التنفيذ"""
        complexity_score = intent_data.get("complexity_score", 5)
        is_multi_step = intent_data.get("multi_step", False)
        urgency = intent_data.get("modifiers", {}).get("urgency", "medium")
        
        if complexity_score >= 8 or is_multi_step:
            strategy = "multi_agent_sequential"
        elif urgency == "urgent":
            strategy = "fast_track_parallel"
        elif complexity_score <= 3:
            strategy = "single_agent_direct"
        else:
            strategy = "standard_hierarchical"
        
        return {
            "strategy_type": strategy,
            "reasoning": f"Based on complexity: {complexity_score}, multi-step: {is_multi_step}, urgency: {urgency}",
            "parallel_execution": urgency == "urgent" and complexity_score < 7,
            "quality_priority": urgency != "urgent"
        }
    
    def _plan_execution_steps(self, intent_data: Dict, strategy: Dict) -> List[Dict]:
        """تخطيط خطوات التنفيذ"""
        primary_intent = intent_data.get("primary_intent", "unknown")
        secondary_intent = intent_data.get("secondary_intent", "unknown")
        
        steps = []
        
        # خطوة التحليل (دائماً أولى)
        steps.append({
            "step_number": 1,
            "step_name": "Deep Analysis",
            "description": "Complete analysis of user request and context",
            "required_agents": ["Intent Analysis Agent", "Context Memory Agent"],
            "estimated_duration": "30 seconds",
            "deliverable": "Comprehensive analysis report"
        })
        
        # خطوات التنفيذ حسب النوع
        if secondary_intent == "email":
            steps.extend(self._plan_email_steps())
        elif secondary_intent == "whatsapp":
            steps.extend(self._plan_whatsapp_steps())
        elif secondary_intent in ["database", "data"]:
            steps.extend(self._plan_database_steps())
        elif secondary_intent == "file":
            steps.extend(self._plan_file_creation_steps())
        else:
            steps.extend(self._plan_general_steps())
        
        # خطوة ضمان الجودة (دائماً أخيرة)
        steps.append({
            "step_number": len(steps) + 1,
            "step_name": "Quality Assurance",
            "description": "Review and validate all outputs",
            "required_agents": ["Quality Assurance Agent"],
            "estimated_duration": "20 seconds",
            "deliverable": "Quality-assured final output"
        })
        
        return steps
    
    def _plan_email_steps(self) -> List[Dict]:
        """خطوات إرسال الإيميل"""
        return [
            {
                "step_number": 2,
                "step_name": "Content Creation",
                "description": "Create personalized email content",
                "required_agents": ["Enhanced Content Agent"],
                "estimated_duration": "45 seconds",
                "deliverable": "Draft email content"
            },
            {
                "step_number": 3,
                "step_name": "Content Enhancement",
                "description": "Enhance content with knowledge base insights",
                "required_agents": ["Knowledge Enhanced Content Agent"],
                "estimated_duration": "30 seconds",
                "deliverable": "Enhanced email content"
            },
            {
                "step_number": 4,
                "step_name": "Email Delivery",
                "description": "Send email using appropriate service",
                "required_agents": ["Email Agent"],
                "estimated_duration": "15 seconds",
                "deliverable": "Delivery confirmation"
            }
        ]
    
    def _plan_whatsapp_steps(self) -> List[Dict]:
        """خطوات إرسال الواتساب"""
        return [
            {
                "step_number": 2,
                "step_name": "Message Creation",
                "description": "Create personalized WhatsApp message",
                "required_agents": ["Enhanced Content Agent"],
                "estimated_duration": "30 seconds",
                "deliverable": "Draft WhatsApp message"
            },
            {
                "step_number": 3,
                "step_name": "Message Enhancement",
                "description": "Enhance message with context and personalization",
                "required_agents": ["Knowledge Enhanced Content Agent"],
                "estimated_duration": "20 seconds",
                "deliverable": "Enhanced WhatsApp message"
            },
            {
                "step_number": 4,
                "step_name": "WhatsApp Delivery",
                "description": "Send message via WhatsApp service",
                "required_agents": ["WhatsApp Agent"],
                "estimated_duration": "10 seconds",
                "deliverable": "Delivery confirmation"
            }
        ]
    
    def _plan_database_steps(self) -> List[Dict]:
        """خطوات قاعدة البيانات"""
        return [
            {
                "step_number": 2,
                "step_name": "Database Operation",
                "description": "Execute database query or operation",
                "required_agents": ["Database Agent"],
                "estimated_duration": "20 seconds",
                "deliverable": "Database operation result"
            }
        ]
    
    def _plan_file_creation_steps(self) -> List[Dict]:
        """خطوات إنشاء الملفات"""
        return [
            {
                "step_number": 2,
                "step_name": "File Content Preparation",
                "description": "Prepare content for file creation",
                "required_agents": ["Enhanced Content Agent"],
                "estimated_duration": "40 seconds",
                "deliverable": "Structured file content"
            },
            {
                "step_number": 3,
                "step_name": "File Generation",
                "description": "Create the requested file format",
                "required_agents": ["File Creation Agent"],
                "estimated_duration": "25 seconds",
                "deliverable": "Generated file"
            }
        ]
    
    def _plan_general_steps(self) -> List[Dict]:
        """خطوات عامة"""
        return [
            {
                "step_number": 2,
                "step_name": "Task Execution",
                "description": "Execute the requested task",
                "required_agents": ["Most Appropriate Agent"],
                "estimated_duration": "45 seconds",
                "deliverable": "Task completion result"
            }
        ]
    
    def _identify_required_resources(self, intent_data: Dict, execution_steps: List[Dict]) -> Dict:
        """تحديد الموارد المطلوبة"""
        required_agents = set()
        estimated_tokens = 0
        
        for step in execution_steps:
            required_agents.update(step.get("required_agents", []))
            estimated_tokens += 200  # تقدير أولي
        
        return {
            "required_agents": list(required_agents),
            "estimated_token_usage": estimated_tokens,
            "external_services": self._identify_external_services(intent_data),
            "database_access": "MongoDB" if any("database" in str(step) for step in execution_steps) else None
        }
    
    def _identify_external_services(self, intent_data: Dict) -> List[str]:
        """تحديد الخدمات الخارجية المطلوبة"""
        services = []
        secondary_intent = intent_data.get("secondary_intent", "")
        
        if secondary_intent == "email":
            services.append("MailerSend")
        elif secondary_intent == "whatsapp":
            services.append("WhatsApp API")
        elif secondary_intent == "call":
            services.append("Call Service")
        
        return services
    
    def _estimate_execution_time(self, execution_steps: List[Dict]) -> Dict:
        """تقدير وقت التنفيذ"""
        total_seconds = sum(
            int(step.get("estimated_duration", "30 seconds").split()[0]) 
            for step in execution_steps
        )
        
        return {
            "total_estimated_time": f"{total_seconds} seconds",
            "breakdown": {step["step_name"]: step["estimated_duration"] for step in execution_steps},
            "confidence_level": "medium"
        }
    
    def _define_success_criteria(self, intent_data: Dict) -> List[str]:
        """تحديد معايير النجاح"""
        criteria = [
            "Task completed without errors",
            "User intent fully satisfied",
            "Quality standards met"
        ]
        
        if intent_data.get("modifiers", {}).get("urgency") == "urgent":
            criteria.append("Completed within time constraint")
        
        if intent_data.get("complexity_score", 0) >= 7:
            criteria.append("All complex requirements addressed")
        
        return criteria
    
    def _define_quality_checkpoints(self, execution_steps: List[Dict]) -> List[Dict]:
        """تحديد نقاط فحص الجودة"""
        checkpoints = []
        
        for i, step in enumerate(execution_steps):
            if "Content" in step["step_name"] or "Enhancement" in step["step_name"]:
                checkpoints.append({
                    "after_step": i + 1,
                    "checkpoint_name": f"Quality Check: {step['step_name']}",
                    "validation_criteria": [
                        "Content accuracy",
                        "Language appropriateness", 
                        "User requirements satisfaction"
                    ]
                })
        
        return checkpoints

class AgentSelectorTool(BaseTool):
    name: str = "Agent Selector Tool"
    description: str = "Selects the most appropriate agents for specific tasks"
    
    def _run(self, task_requirements: str, available_agents: str = None) -> str:
        """اختيار الوكلاء المناسبين للمهمة"""
        # نسخة مبسطة للبداية
        return json.dumps({
            "recommended_agents": ["Intent Analysis Agent", "Context Memory Agent", "Enhanced Content Agent"],
            "reasoning": "Based on task analysis",
            "confidence": 0.8
        }, ensure_ascii=False)

class RiskAssessmentTool(BaseTool):
    name: str = "Risk Assessment Tool"  
    description: str = "Assesses potential risks and prepares mitigation strategies"
    
    def _run(self, execution_plan: str, user_context: str = "") -> str:
        """تقييم المخاطر - نسخة مبسطة"""
        return json.dumps({
            "risk_level": "low",
            "identified_risks": [],
            "mitigation_strategies": [],
            "contingency_plans": []
        }, ensure_ascii=False)
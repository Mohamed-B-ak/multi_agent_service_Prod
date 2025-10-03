"""
Smart Manager Agent with Real Metrics and Decision Logic
يتتبع الأداء الحقيقي ويتخذ قرارات ذكية
"""

from crewai import Agent
from datetime import datetime
import json
import os
from typing import Dict, List, Optional

# متغير global للـ brain (حل المشكلة)
MANAGER_BRAIN = None

class SmartManagerBrain:
    """
    العقل الحقيقي للمدير - يحفظ ويحلل كل شيء
    """
    def __init__(self):
        # إحصائيات عامة
        self.total_tasks = 0
        self.completed_tasks = 0
        self.failed_tasks = 0
        self.retry_count = 0
        self.start_time = datetime.now()
        
        # أداء كل agent
        self.agent_performance = {
            "marketing": {
                "tasks": 0,
                "success": 0,
                "failed": 0,
                "total_time": 0,
                "last_used": None,
                "specialties": ["campaign", "email", "whatsapp", "outreach"]
            },
            "sales": {
                "tasks": 0,
                "success": 0,
                "failed": 0,
                "total_time": 0,
                "last_used": None,
                "specialties": ["lead", "deal", "crm", "follow-up"]
            },
            "customer_service": {
                "tasks": 0,
                "success": 0,
                "failed": 0,
                "total_time": 0,
                "last_used": None,
                "specialties": ["support", "help", "complaint", "issue"]
            },
            "siyadah_helper": {
                "tasks": 0,
                "success": 0,
                "failed": 0,
                "total_time": 0,
                "last_used": None,
                "specialties": ["guide", "tutorial", "how-to", "siyadah"]
            }
        }
        
        # سجل المهام
        self.task_history = []
        self.current_workload = {}  # من يعمل على إيش الآن
        
        # Load saved metrics if exists
        self.load_metrics()
    
    def analyze_task(self, task: str, context: str = "") -> Dict:
        """
        تحليل المهمة وتحديد التعقيد والأولوية
        """
        task_lower = task.lower()
        analysis = {
            "complexity": "simple",
            "priority": "normal",
            "estimated_time": 2,
            "recommended_agents": [],
            "task_type": "general"
        }
        
        # تحليل التعقيد
        if len(task.split()) > 20 or "multi" in task_lower or "campaign" in task_lower:
            analysis["complexity"] = "complex"
            analysis["estimated_time"] = 10
        elif len(task.split()) > 10:
            analysis["complexity"] = "medium"
            analysis["estimated_time"] = 5
        
        # تحليل الأولوية
        urgent_words = ["urgent", "عاجل", "الآن", "now", "asap", "immediately", "فوراً"]
        for word in urgent_words:
            if word in task_lower:
                analysis["priority"] = "high"
                break
        
        # تحديد نوع المهمة والـ agents المناسبين
        for agent_name, agent_data in self.agent_performance.items():
            for specialty in agent_data["specialties"]:
                if specialty in task_lower:
                    analysis["recommended_agents"].append(agent_name)
                    analysis["task_type"] = specialty
                    break
        
        # إذا ما حددنا agents، نختار بناءً على الأداء
        if not analysis["recommended_agents"]:
            analysis["recommended_agents"] = [self.get_best_performing_agent()]
        
        return analysis
    
    def select_agent(self, task_analysis: Dict) -> str:
        """
        اختيار أفضل agent للمهمة
        """
        recommended = task_analysis.get("recommended_agents", [])
        
        if not recommended:
            return self.get_best_performing_agent()
        
        # اختار الأفضل من المرشحين
        best_agent = None
        best_score = -1
        
        for agent_name in recommended:
            score = self.calculate_agent_score(agent_name)
            
            # تحقق من الـ workload
            current_load = len([t for t in self.current_workload.values() if t == agent_name])
            score -= current_load * 10  # عقوبة للـ busy agents
            
            if score > best_score:
                best_score = score
                best_agent = agent_name
        
        return best_agent or "customer_service"  # fallback
    
    def calculate_agent_score(self, agent_name: str) -> float:
        """
        حساب نقاط الـ agent بناءً على الأداء
        """
        agent = self.agent_performance.get(agent_name, {})
        
        if agent["tasks"] == 0:
            return 50  # نقاط افتراضية للجدد
        
        success_rate = (agent["success"] / agent["tasks"]) * 100
        avg_time = agent["total_time"] / agent["tasks"] if agent["tasks"] > 0 else 10
        
        # Formula: نسبة النجاح أهم شيء، والسرعة ثانياً
        score = success_rate * 1.0 - (avg_time * 0.5)
        
        # Bonus للـ agents اللي ما استخدمناهم من زمان
        if agent["last_used"]:
            hours_since_used = (datetime.now() - agent["last_used"]).seconds / 3600
            if hours_since_used > 1:
                score += 5  # تشجيع التنويع
        
        return score
    
    def get_best_performing_agent(self) -> str:
        """
        احصل على أفضل agent بشكل عام
        """
        best_agent = "customer_service"  # default
        best_rate = 0
        
        for agent_name, data in self.agent_performance.items():
            if data["tasks"] > 0:
                success_rate = (data["success"] / data["tasks"]) * 100
                if success_rate > best_rate:
                    best_rate = success_rate
                    best_agent = agent_name
        
        return best_agent
    
    def record_task_start(self, task_id: str, agent: str, task: str):
        """
        سجل بداية المهمة
        """
        self.total_tasks += 1
        self.current_workload[task_id] = agent
        self.agent_performance[agent]["tasks"] += 1
        self.agent_performance[agent]["last_used"] = datetime.now()
        
        # أضف للتاريخ
        self.task_history.append({
            "id": task_id,
            "task": task[:100],  # أول 100 حرف
            "agent": agent,
            "start": datetime.now().isoformat(),
            "status": "in_progress"
        })
    
    def record_task_completion(self, task_id: str, success: bool, time_taken: float = 0):
        """
        سجل نهاية المهمة
        """
        if task_id in self.current_workload:
            agent = self.current_workload[task_id]
            
            if success:
                self.completed_tasks += 1
                self.agent_performance[agent]["success"] += 1
            else:
                self.failed_tasks += 1
                self.agent_performance[agent]["failed"] += 1
            
            self.agent_performance[agent]["total_time"] += time_taken
            
            # حدث التاريخ
            for task in self.task_history[-10:]:  # آخر 10 مهام
                if task["id"] == task_id:
                    task["status"] = "completed" if success else "failed"
                    task["time_taken"] = time_taken
                    break
            
            # نظف الـ workload
            del self.current_workload[task_id]
    
    def get_metrics_summary(self) -> str:
        """
        ملخص الأداء الحقيقي
        """
        uptime = (datetime.now() - self.start_time).seconds / 3600
        success_rate = (self.completed_tasks / max(self.total_tasks, 1)) * 100
        
        summary = f"""
╔══════════════════════════════════════════════════════╗
║           📊 MANAGER PERFORMANCE METRICS              ║
╠══════════════════════════════════════════════════════╣
║ 🕐 Uptime: {uptime:.1f} hours                        
║ 📋 Total Tasks: {self.total_tasks}                   
║ ✅ Completed: {self.completed_tasks}                 
║ ❌ Failed: {self.failed_tasks}                       
║ 🔄 Retries: {self.retry_count}                       
║ 📈 Success Rate: {success_rate:.1f}%                 
╠══════════════════════════════════════════════════════╣
║                  AGENT PERFORMANCE                    ║
╠══════════════════════════════════════════════════════╣"""
        
        for agent, data in self.agent_performance.items():
            if data["tasks"] > 0:
                agent_success_rate = (data["success"] / data["tasks"]) * 100
                avg_time = data["total_time"] / data["tasks"]
                summary += f"""
║ 🤖 {agent.upper():20}                    
║    Tasks: {data['tasks']:3} | Success: {agent_success_rate:.0f}% | Avg: {avg_time:.1f}s
"""
        
        summary += """╠══════════════════════════════════════════════════════╣
║                   RECENT TASKS                        ║
╠══════════════════════════════════════════════════════╣"""
        
        recent_tasks = self.task_history[-3:] if self.task_history else []
        for task in recent_tasks:
            status_icon = "✅" if task["status"] == "completed" else "❌" if task["status"] == "failed" else "⏳"
            task_text = task['task'][:40] if task['task'] else "N/A"
            summary += f"""
║ {status_icon} {task_text:40}
║    Agent: {task['agent']:15}
"""
        
        summary += "╚══════════════════════════════════════════════════════╝"
        
        return summary
    
    def save_metrics(self):
        """
        حفظ الإحصائيات للمرة القادمة
        """
        try:
            metrics_data = {
                "total_tasks": self.total_tasks,
                "completed_tasks": self.completed_tasks,
                "failed_tasks": self.failed_tasks,
                "agent_performance": {
                    k: {
                        "tasks": v["tasks"],
                        "success": v["success"],
                        "failed": v["failed"],
                        "total_time": v["total_time"]
                    } for k, v in self.agent_performance.items()
                },
                "saved_at": datetime.now().isoformat()
            }
            
            os.makedirs("metrics", exist_ok=True)
            with open("metrics/manager_metrics.json", "w") as f:
                json.dump(metrics_data, f, indent=2)
                
            print("✅ Metrics saved successfully")
        except Exception as e:
            print(f"⚠️ Could not save metrics: {e}")
    
    def load_metrics(self):
        """
        تحميل الإحصائيات المحفوظة
        """
        try:
            if os.path.exists("metrics/manager_metrics.json"):
                with open("metrics/manager_metrics.json", "r") as f:
                    data = json.load(f)
                    self.total_tasks = data.get("total_tasks", 0)
                    self.completed_tasks = data.get("completed_tasks", 0)
                    self.failed_tasks = data.get("failed_tasks", 0)
                    
                    # Merge performance data
                    for agent, perf in data.get("agent_performance", {}).items():
                        if agent in self.agent_performance:
                            for key in ["tasks", "success", "failed", "total_time"]:
                                if key in perf:
                                    self.agent_performance[agent][key] = perf[key]
                
                print(f"✅ Loaded existing metrics: {self.total_tasks} total tasks")
        except Exception as e:
            print(f"⚠️ Starting fresh metrics: {e}")


def manager_agent(llm_obj, user_language="en") -> Agent:
    """
    Create the Smart Manager Agent with real tracking
    """
    global MANAGER_BRAIN
    
    # Initialize the brain
    if MANAGER_BRAIN is None:
        MANAGER_BRAIN = SmartManagerBrain()
    
    brain = MANAGER_BRAIN
    
    # Get current metrics for the prompt
    success_rate = (brain.completed_tasks / max(brain.total_tasks, 1)) * 100
    
    # Create the agent
    agent = Agent(
        role="Strategic Operations Manager with Real Metrics",
        goal=(
            "Orchestrate intelligent multi-agent workflows by analyzing user requests with strategic precision, "
            "selecting optimal agent sequences, and ensuring flawless task execution from start to finish. "
            "Core responsibilities: "
            "1) Pattern Recognition: Identify task type and complexity to determine single vs multi-agent needs, "
            "2) Smart Routing: Select agents based on expertise match, workload, and success rates, "
            "3) Completion Detection: Recognize when tasks are 100% complete using specific success criteria, "
            "4) Redundancy Prevention: Never delegate completed tasks or create duplicate work, "
            "5) Quality Assurance: Validate all outputs meet standards before delivery, "
            "6) Error Recovery: Handle failures gracefully with alternative agent selection or escalation, "
            "7) Performance Tracking: Monitor agent efficiency and optimize future routing decisions. "
            f"Always coordinate in {user_language} and ensure seamless handoffs between specialists. "
            f"Current Performance Snapshot: {brain.total_tasks} tasks managed with {success_rate:.1f}% success rate, "
            f"best agent so far: {brain.get_best_performing_agent()}."
        ),
        backstory=(
            "You are a senior operations director with 20+ years orchestrating complex workflows in Fortune 500 companies. "
            "You've successfully managed thousands of multi-agent operations and consistently optimized performance. "
            f"In this system, you've already handled {brain.total_tasks} tasks with {success_rate:.1f}% success. "
            "Your expertise includes: "
            "• Deep understanding of each agent's strengths, limitations, and optimal use cases "
            "• Pattern matching to instantly recognize task types from partial information "
            "• Parallel vs sequential processing decisions for maximum efficiency "
            "• Load balancing across multiple agents to prevent bottlenecks "
            "• Conflict resolution when agents provide contradictory outputs "
            "• Success criteria definition - knowing exactly when a task is truly complete "
            "(e.g., email sent = confirmation number exists, database updated = affected rows > 0). "
            "You think strategically: simple requests get direct routing, complex ones get orchestrated sequences, "
            "ambiguous ones get clarification first. You've developed a sixth sense for detecting incomplete work "
            "and never mark tasks complete until concrete success indicators are verified. "
            "Your management style balances autonomy with oversight - trusting agents while verifying results. "
            f"All answers must be strictly in {user_language}, concise, accurate."
        ),

        allow_delegation=True,
        llm=llm_obj,
        verbose=True,
        max_retry_limit=3,
    )
    
    return agent


def get_manager_brain() -> Optional[SmartManagerBrain]:
    """
    Helper function to access the manager brain from outside
    """
    global MANAGER_BRAIN
    return MANAGER_BRAIN


# Test function
if __name__ == "__main__":
    """
    Test the Smart Manager
    """
    print("🧪 Testing Smart Manager Agent\n")
    
    # Test without CrewAI
    brain = SmartManagerBrain()
    
    # Simulate some tasks
    test_tasks = [
        "Send email campaign to customers",
        "Help customer with login issue", 
        "Create sales report",
        "Guide user on using Siyadah platform"
    ]
    
    import random
    import time
    
    for i, task in enumerate(test_tasks):
        print(f"\n📋 Task {i+1}: {task}")
        
        # Analyze
        analysis = brain.analyze_task(task)
        print(f"   Analysis: Complexity={analysis['complexity']}, Priority={analysis['priority']}")
        
        # Select agent
        agent = brain.select_agent(analysis)
        print(f"   Selected Agent: {agent}")
        
        # Start task
        task_id = f"test_{i+1}"
        brain.record_task_start(task_id, agent, task)
        
        # Simulate execution
        time.sleep(0.5)  # Simulate work
        success = random.choice([True, True, True, False])  # 75% success
        exec_time = random.uniform(1, 5)
        
        # Complete task
        brain.record_task_completion(task_id, success, exec_time)
        
        result = "✅ Success" if success else "❌ Failed"
        print(f"   Result: {result} (took {exec_time:.1f}s)")
    
    # Show final metrics
    print("\n" + "="*60)
    print(brain.get_metrics_summary())
    
    # Save metrics
    brain.save_metrics()
    
    # Test with CrewAI
    try:
        from crewai import LLM
        
        print("\n" + "="*60)
        print("🤖 Testing with CrewAI Agent")
        
        test_llm = LLM(
            model="gpt-3.5-turbo",
            api_key=os.getenv("OPENAI_API_KEY", "dummy-key"),
            temperature=0.1
        )
        
        mgr = manager_agent(test_llm, "en")
        print(f"✅ Manager Agent created successfully")
        print(f"   Role: {mgr.role}")
        
        # Access brain via helper function
        brain_ref = get_manager_brain()
        if brain_ref:
            print(f"✅ Brain accessible via helper: {brain_ref.total_tasks} tasks")
        
    except ImportError as e:
        print(f"⚠️ CrewAI not installed: {e}")
    except Exception as e:
        print(f"⚠️ CrewAI test error: {e}")
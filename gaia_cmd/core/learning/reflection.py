import logging
import json
from typing import Dict, Any, List, Optional
from gaia_cmd.core.llm.provider import LLMProvider
from gaia_cmd.core.llm.safe_generate import safe_generate
from gaia_cmd.core.memory.manager import MemoryManager

class ReflectionEngine:
    """
    Advanced Reflection System for Gaia CLI.
    Analyzes task outcomes to evolve Gaia's strategies and thinking patterns.
    Now specifically captures detailed experience entries: Problem, Solution, Errors, and Fixes.
    """
    def __init__(self, llm: LLMProvider, memory: MemoryManager):
        self.llm = llm
        self.memory = memory
        self.logger = logging.getLogger("ReflectionEngine")

    def reflect_on_task(self, task_desc: str, result: Dict[str, Any], step_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Performs a deep reflection after a task is completed (or failed).
        Generates improvement notes, better strategies, and structured experience data.
        """
        self.logger.info(f"Starting deep reflection on task: {task_desc}")
        
        success = result.get("success", False) or result.get("status") == "success"
        
        system_prompt = (
            "You are the Gaia CLI Reflection Module. Your goal is to analyze the recent task execution "
            "to evolve the system's intelligence. Focus on learning from the experience.\n"
            "Analyze:\n"
            "1. Problem: What was the primary goal?\n"
            "2. Errors: What technical errors or roadblocks were encountered?\n"
            "3. Fixes: What specific actions resolved those errors?\n"
            "4. Strategy: What is the optimal approach for this type of task in the future?\n\n"
            "Respond ONLY with a JSON object containing:\n"
            "{\n"
            "  \"analysis\": \"...\",\n"
            "  \"problem\": \"...\",\n"
            "  \"errors\": [\"...\"],\n"
            "  \"fixes\": [\"...\"],\n"
            "  \"new_strategy\": \"...\",\n"
            "  \"tags\": [\"...\"]\n"
            "}"
        )
        
        # Summarize history for reflection context
        history_summary = []
        for turn in step_history:
            role = turn.get("role")
            content = turn.get("content", "")
            if role == "assistant" and "tool" in content:
                try:
                    tool_data = json.loads(content)
                    history_summary.append(f"Action: {tool_data.get('tool')} with {tool_data.get('params')}")
                except:
                    history_summary.append(f"Action: {content[:100]}...")
            elif role == "user" and "TOOL RESULT" in content:
                history_summary.append(f"Result: {content[:200]}...")

        user_prompt = (
            f"TASK: {task_desc}\n"
            f"OUTCOME: {'SUCCESS' if success else 'FAILURE'}\n"
            f"FINAL RESULT/ERROR: {result.get('error', result.get('output', ''))}\n"
            f"EXECUTION LOG SUMMARY:\n" + "\n".join(history_summary) + "\n\n"
            "Provide your structured reflection in JSON format."
        )

        try:
            response_content = safe_generate(self.llm, [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ], task_description=f"Reflecting on: {task_desc}")
            
            response_text = response_content.get("content", "")

            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0].strip()
            elif "{" in response_text:
                json_str = response_text[response_text.find("{"):response_text.rfind("}")+1]
            else:
                json_str = "{}"
            
            reflection = json.loads(json_str)
            
            # Feed reflection back into the systems
            self._apply_reflection(task_desc, success, reflection)
            
            return reflection
            
        except Exception as e:
            self.logger.error(f"Reflection failed: {e}")
            return {"error": str(e)}

    def _apply_reflection(self, task: str, success: bool, reflection: Dict[str, Any]):
        """
        Persists the reflection results into the Memory systems.
        """
        analysis = reflection.get("analysis", "")
        problem = reflection.get("problem", task)
        errors = reflection.get("errors", [])
        fixes = reflection.get("fixes", [])
        strategy = reflection.get("new_strategy", "")
        tags = reflection.get("tags", []) + ["reflection"]
        
        # 1. Save refined experience to persistent memory
        self.memory.persistent.save_experience(
            problem=problem,
            solution=strategy,
            errors=errors,
            fixes=fixes
        )
        
        # 2. Store in Global Memory for cross-project insights
        insight = f"REFLECTIVE ANALYSIS: {analysis}\nOPTIMIZED STRATEGY: {strategy}"
        if errors:
            insight += f"\nERRORS ENCOUNTERED: {', '.join(errors)}"
        
        self.memory.learn_from_feedback(
            task=task,
            success=success,
            diagnosis=insight,
            tags=tags
        )
        
        # 3. Store specific architectural patterns if high value
        if strategy and "architecture" in tags:
            self.memory.long_term.add_insight("patterns", f"Optimized Strategy for '{task}': {strategy}")

        self.logger.info(f"Experience system updated for task: {task}")

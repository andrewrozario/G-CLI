import logging
import os
from typing import Dict, Any, List, Optional
from gaia_cmd.core.learning.evaluator import PerformanceScore, LessonLearner

class SelfImprovementManager:
    """
    Orchestrates the feedback loop and self-learning for Gaia CLI.
    Analyses performance after each task and optimizes behavior.
    """
    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root
        self.logger = logging.getLogger("SelfImprovement")
        self.learner = LessonLearner(workspace_root)
        self.total_scores: List[int] = []

    def record_task_outcome(self, task: Dict[str, Any], result: Dict[str, Any], attempts: int, duration: float, diagnosis: Optional[str] = None) -> PerformanceScore:
        """
        Finalizes a task by scoring it, learning lessons, and persisting knowledge.
        """
        # 1. Score the execution
        score = PerformanceScore(
            task_id=task.get("id", "unknown"),
            success=result.get("status") == "success" or result.get("success", False),
            attempts=attempts,
            time_taken=duration
        )
        self.total_scores.append(score.score)
        self.logger.info(f"Task scored: {score.score}/100 [Attempts: {attempts}]")

        # 2. Extract lessons from the result
        self.learner.extract_lesson(task, result, diagnosis)
        
        return score

    def get_behavioral_adjustment(self) -> str:
        """
        Analyzes historical lessons to generate an 'adjustment block' for the LLM.
        This provides a dynamic 'Self-Correction' layer to the prompt.
        """
        lessons = self.learner.get_top_lessons(limit=5)
        if not lessons:
            return ""
            
        adjustment = "\n### HISTORICAL PERFORMANCE LESSONS (SELF-IMPROVEMENT) ###\n"
        adjustment += "In recent tasks, you have learned the following lessons:\n"
        for lesson in lessons:
            adjustment += f"- {lesson}\n"
        adjustment += "\nUse these insights to refine your strategy for the current task."
        return adjustment

    def get_average_performance(self) -> float:
        """Returns the average score over all tasks."""
        if not self.total_scores:
            return 0.0
        return sum(self.total_scores) / len(self.total_scores)

    def trigger_self_code_review(self):
        """
        Placeholder for the capability to audit Gaia's own core files if 
        performance drops below a threshold.
        """
        avg_performance = self.get_average_performance()
        if avg_performance < 50 and len(self.total_scores) > 5:
            self.logger.warning("Low performance detected. Self-audit of Gaia codebase suggested.")
            # This would trigger a specialized 'Gaia: Audit Thyself' task
            return True
        return False

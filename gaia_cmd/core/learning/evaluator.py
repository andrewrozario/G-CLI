import logging
import json
import os
import time
from typing import Dict, Any, List, Optional

class PerformanceScore:
    """Represents a score for a single task execution."""
    def __init__(self, task_id: str, success: bool, attempts: int, time_taken: float):
        self.task_id = task_id
        self.success = success
        self.attempts = attempts
        self.time_taken = time_taken
        self.score = self._calculate_score()

    def _calculate_score(self) -> int:
        """
        Calculates a score (0-100) based on success and efficiency.
        - Success: +70
        - Fewer Attempts: +30 (max) - (10 * (attempts - 1))
        - Time: (Optional future metric)
        """
        if not self.success:
            return 0
        
        efficiency_bonus = max(0, 30 - (10 * (self.attempts - 1)))
        return 70 + efficiency_bonus

class LessonLearner:
    """
    Extracts high-level lessons from task cycles to improve Gaia's
    future strategies.
    """
    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root
        self.logger = logging.getLogger("LessonLearner")
        self.lessons_file = os.path.join(workspace_root, "memory", "learning", "lessons.json")
        self._ensure_storage()

    def _ensure_storage(self):
        os.makedirs(os.path.dirname(self.lessons_file), exist_ok=True)
        if not os.path.exists(self.lessons_file):
            with open(self.lessons_file, "w") as f:
                json.dump([], f)

    def extract_lesson(self, task: Dict[str, Any], result: Dict[str, Any], diagnosis: Optional[str] = None) -> Dict[str, Any]:
        """
        Creates a lesson based on what happened.
        """
        lesson = {
            "timestamp": time.time(),
            "task_type": task.get("id", "unknown"),
            "success": result.get("status") == "success",
            "diagnosis": diagnosis,
            "impact": "Avoided repetition" if diagnosis else "Reinforced successful pattern"
        }
        
        self._save_lesson(lesson)
        return lesson

    def _save_lesson(self, lesson: Dict[str, Any]):
        try:
            with open(self.lessons_file, "r") as f:
                lessons = json.load(f)
            lessons.append(lesson)
            # Keep only the last 100 lessons for context efficiency
            lessons = lessons[-100:]
            with open(self.lessons_file, "w") as f:
                json.dump(lessons, f, indent=4)
        except Exception as e:
            self.logger.error(f"Failed to save lesson: {e}")

    def get_top_lessons(self, limit: int = 5) -> List[str]:
        """Returns the most recent lessons as strings for prompt injection."""
        try:
            with open(self.lessons_file, "r") as f:
                lessons = json.load(f)
            # Summarize the last few lessons
            summaries = []
            for l in lessons[-limit:]:
                status = "Success" if l['success'] else "Failure"
                diag = f" - Diagnosis: {l['diagnosis']}" if l['diagnosis'] else ""
                summaries.append(f"[{status}] Task {l['task_type']}{diag}")
            return summaries
        except:
            return []

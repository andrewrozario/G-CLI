import json
import os

class GoalEngine:
    """Manages high-level user goals and persists them."""
    def __init__(self, path: str = "core/autonomy/goals.json"):
        self.path = path
        self.goals = self._load_goals()

    def _load_goals(self) -> list:
        if os.path.exists(self.path):
            with open(self.path, 'r') as f:
                return json.load(f)
        return []

    def add_goal(self, goal: str):
        self.goals.append({"goal": goal, "status": "active"})
        with open(self.path, 'w') as f:
            json.dump(self.goals, f)

    def get_active_goals(self) -> list:
        return [g for g in self.goals if g["status"] == "active"]

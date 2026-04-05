import json
from models import ModelFactory

class TaskGenerator:
    """Uses LLM reasoning to generate self-directed tasks from high-level goals."""
    def __init__(self, model_type: str = "claude"):
        self.client = ModelFactory.get_client(model_type)

    def generate_tasks(self, goals: list, context: str = "") -> list:
        goal_list = "\n".join([g["goal"] for g in goals])
        system_prompt = "You are the Gaia Task Generator. Break down high-level goals into concrete, prioritized, actionable tasks for a multi-agent system."
        prompt = f"Active Goals:\n{goal_list}\n\nContext:\n{context}\n\nGenerate a prioritized list of tasks. Respond ONLY in valid JSON format with a 'tasks' key."
        
        response = self.client.generate_json(prompt, system=system_prompt)
        try:
            return json.loads(response).get("tasks", [])
        except:
            return []

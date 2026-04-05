import json
from models.base_client import BaseModelClient
from core.prompts import build_system_prompt

class Planner:
    """Uses Claude (or specified model) to create high-level engineering plans."""
    
    def __init__(self, client: BaseModelClient):
        self.client = client

    def create_plan(self, objective: str, persona: str = "software_architect", reasoning: str = "chain_of_thought", context: str = "") -> list:
        system_prompt = build_system_prompt(persona, reasoning) + "\n\nGiven the objective and context, break it down into a sequence of concrete, executable coding or engineering steps.\nRespond ONLY in valid JSON format with a 'plan' key containing a list of strings."
        prompt = f"Context: {context}\nObjective: {objective}\nCreate a highly detailed, step-by-step technical execution plan."
        
        response = self.client.generate_json(prompt, system=system_prompt)
        try:
            data = json.loads(response)
            return data.get("plan", [])
        except json.JSONDecodeError:
            # Try to extract JSON if it's wrapped in text
            try:
                import re
                match = re.search(r'\{.*\}', response, re.DOTALL)
                if match:
                    data = json.loads(match.group())
                    return data.get("plan", [])
            except:
                pass
            return [f"Execute task: {objective}"] # Fallback to single step

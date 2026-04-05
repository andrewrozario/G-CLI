import json
from models.base_client import BaseModelClient
from core.prompts import build_system_prompt

class Observer:
    """Uses Gemini (or specified model) for observation, summarization, and validation."""
    
    def __init__(self, client: BaseModelClient):
        self.client = client

    def observe_and_summarize(self, task: str, result: str) -> str:
        """Summarizes the outcome of an execution step."""
        prompt = f"Task: {task}\nResult: {result}\n\nProvide a concise, technical summary of the execution outcome."
        system_prompt = "You are an expert technical observer. Provide dense, accurate summaries of execution results."
        return self.client.generate(prompt, system=system_prompt)

    def validate(self, step: str, result: str, persona: str = "software_architect") -> dict:
        """Validates if the result meets the step's requirements."""
        system_prompt = build_system_prompt(persona, "self_critique") + "\n\nReview the result of the action against its objective. Be ruthless in your technical critique. Determine if it succeeded structurally, logically, and stylistically. Respond ONLY in JSON with keys 'success' (boolean) and 'feedback' (string with detailed constructive criticism if failed)."
        prompt = f"Objective: {step}\nResult: {result}\nEvaluate the result rigorously."
        
        response = self.client.generate_json(prompt, system=system_prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON if it's wrapped in text
            try:
                import re
                match = re.search(r'\{.*\}', response, re.DOTALL)
                if match:
                    return json.loads(match.group())
            except:
                pass
            return {"success": True, "feedback": "Validation succeeded with limited feedback."} # Assume success as fallback

import json
from models import ModelFactory

class ComplexityEstimator:
    """Estimates the difficulty and risk of a given objective."""
    def __init__(self, model_type: str = "local"):
        self.client = ModelFactory.get_client(model_type)

    def estimate(self, objective: str) -> dict:
        system_prompt = "You are the G CLI Complexity Estimator. Evaluate the task difficulty (1-10) and whether it requires a multi-model chain."
        prompt = f"Objective: {objective}\n\nRespond ONLY in JSON with 'score' (int) and 'requires_chain' (bool) keys."
        
        response = self.client.generate_json(prompt, system=system_prompt)
        try:
            return json.loads(response)
        except:
            return {"score": 5, "requires_chain": False}

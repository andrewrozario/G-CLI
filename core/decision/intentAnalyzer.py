import json
from models import ModelFactory

class IntentAnalyzer:
    """Analyzes the core purpose of user input to determine task types."""
    def __init__(self, model_type: str = "local"):
        self.client = ModelFactory.get_client(model_type)

    def analyze(self, objective: str) -> dict:
        # Quick heuristic for paths
        import os
        words = objective.split()
        detected_path = None
        for word in words:
            if "/" in word or "\\" in word:
                clean_path = word.strip("'\"")
                if os.path.exists(clean_path):
                    detected_path = clean_path
                    break

        system_prompt = "You are the G CLI Intent Analyzer. Classify the user input into specific intents (coding, architectural, research, debugging, summarization, system_study)."
        prompt = f"Objective: {objective}\n\nRespond ONLY in JSON with 'intent' and 'sub_intent' keys."
        
        response = self.client.generate_json(prompt, system=system_prompt)
        try:
            data = json.loads(response)
            if detected_path:
                data["intent"] = "system_study"
                data["path"] = detected_path
            return data
        except:
            return {"intent": "coding", "sub_intent": "general"}

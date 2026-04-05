import json
from models import GeminiClient

class TaskClassifier:
    def __init__(self, llm: GeminiClient = None):
        self.llm = llm or GeminiClient(model_name="gemini-1.5-flash")
        self.system_prompt = """You are the G CLI Intent Parser.
Your job is to classify the user objective into one or more task categories.

Categories:
- reasoning: complex logical deduction, architectural planning, system design.
- coding: generating code, boilerplate, implementation of specific functions.
- debugging: fixing errors, analyzing logs, finding bugs.
- summarization: condensing large amounts of text or data.
- multimodal: tasks involving images, video, or audio (scanning UI, etc).
- system_operations: file management, shell commands, git operations.

Analyze the input and provide:
1. Primary category
2. Complexity score (1-10)
3. Reasoning requirement (true/false)
4. Precision requirement (true/false)

Respond ONLY in JSON format:
{
    "category": "primary_category",
    "complexity": 5,
    "needs_reasoning": true,
    "needs_precision": true,
    "is_multimodal": false
}"""

    def classify(self, objective: str) -> dict:
        prompt = f"Objective: {objective}\nClassify this task."
        response = self.llm.generate_json(prompt, system=self.system_prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback
            return {
                "category": "coding",
                "complexity": 5,
                "needs_reasoning": True,
                "needs_precision": True,
                "is_multimodal": False
            }

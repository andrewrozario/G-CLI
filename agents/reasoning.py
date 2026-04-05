import json
from core.llm_client import LocalLLMClient
from core.prompts import build_system_prompt, CODING_PERSONAS, REASONING_FRAMEWORKS

class ExpertiseRouter:
    def __init__(self, llm: LocalLLMClient):
        self.llm = llm
        self.system_prompt = f"""You are the Gaia Cognitive Routing Brain.
Your job is to analyze the user objective and select the best domain expertise (persona) and reasoning framework.
Available Personas: {list(CODING_PERSONAS.keys())}
Available Reasoning Frameworks: {list(REASONING_FRAMEWORKS.keys())}

Respond ONLY in JSON format:
{{
    "persona": "selected_persona",
    "reasoning": "selected_framework"
}}"""

    def route(self, objective: str) -> dict:
        prompt = f"Objective: {objective}\nSelect the optimal persona and reasoning framework for this exact task."
        response = self.llm.generate_json(prompt, system=self.system_prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback to safe defaults
            return {"persona": "software_architect", "reasoning": "chain_of_thought"}

class AdvancedPlannerAgent:
    def __init__(self, llm: LocalLLMClient):
        self.llm = llm

    def create_plan(self, objective: str, persona: str, reasoning: str, context: str = "") -> list:
        system_prompt = build_system_prompt(persona, reasoning) + "\n\nGiven the objective and context, break it down into a sequence of concrete, executable coding or engineering steps.\nRespond ONLY in valid JSON format with a 'plan' key containing a list of strings."
        prompt = f"Context: {context}\nObjective: {objective}\nCreate a highly detailed, step-by-step technical execution plan."
        response = self.llm.generate_json(prompt, system=system_prompt)
        try:
            data = json.loads(response)
            return data.get("plan", [])
        except json.JSONDecodeError:
            return []

class AdvancedCriticAgent:
    def __init__(self, llm: LocalLLMClient):
        self.llm = llm

    def evaluate(self, objective: str, result: str, persona: str) -> dict:
        system_prompt = build_system_prompt(persona, "self_critique") + "\n\nReview the result of the action against its objective. Be ruthless in your technical critique. Determine if it succeeded structurally, logically, and stylistically. Respond ONLY in JSON with keys 'success' (boolean) and 'feedback' (string with detailed constructive criticism if failed)."
        prompt = f"Objective: {objective}\nResult: {result}\nEvaluate the result rigorously."
        response = self.llm.generate_json(prompt, system=system_prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"success": False, "feedback": "Critique failed to parse."}

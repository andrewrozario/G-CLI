from models.base_client import BaseModelClient
from core.prompts import build_system_prompt

class Executor:
    """Uses Codex (GPT-4o) for high-precision code implementation and debugging."""
    
    def __init__(self, client: BaseModelClient):
        self.client = client

    def execute_step(self, step: str, strategy: str = "", context: str = "", persona: str = "software_architect") -> str:
        system_prompt = build_system_prompt(persona, "chain_of_thought") + "\n\nYou are an implementation expert. Perform the following task with high precision."
        prompt = f"Step to execute: {step}\nStrategic Roadmap: {strategy}\nContext: {context}\n\nExecute the step and provide the implementation or solution."
        
        return self.client.generate(prompt, system=system_prompt)

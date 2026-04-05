from .baseAgent import BaseAgent

class CoderAgent(BaseAgent):
    """Uses Codex (GPT-4o) for high-precision code implementation and debugging."""
    
    def __init__(self):
        super().__init__("Coder", "Technical Implementation & Debugging", "codex")

    def act(self, task: str, context: str = "") -> str:
        system_prompt = f"Role: {self.role}. You are the G CLI Coder. Implement the following technical requirement with high precision."
        prompt = f"Context: {context}\nTask: {task}\n\nProvide the code or technical fix."
        return self.client.generate(prompt, system=system_prompt)

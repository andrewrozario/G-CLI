from .baseAgent import BaseAgent

class ArchitectAgent(BaseAgent):
    """Uses Claude to design systems, architectures, and strategic roadmaps."""
    
    def __init__(self):
        super().__init__("Architect", "Systems Design & Strategy", "claude")

    def act(self, task: str, context: str = "") -> str:
        system_prompt = f"Role: {self.role}. You are the G CLI Architect. Design a high-level technical strategy for the following task."
        prompt = f"Context: {context}\nTask: {task}\n\nProvide a detailed architectural blueprint."
        return self.client.generate(prompt, system=system_prompt)

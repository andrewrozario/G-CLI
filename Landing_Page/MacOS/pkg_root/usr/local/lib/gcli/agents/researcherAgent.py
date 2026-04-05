from .baseAgent import BaseAgent

class ResearcherAgent(BaseAgent):
    """Uses Gemini for data scanning, summarization, and market insights."""
    
    def __init__(self):
        super().__init__("Researcher", "Data Analysis & Market Research", "gemini")

    def act(self, task: str, context: str = "") -> str:
        system_prompt = f"Role: {self.role}. You are the G CLI Researcher. Scan the context and gather deep insights regarding the task."
        prompt = f"Context: {context}\nTask: {task}\n\nProvide a comprehensive summary of findings."
        return self.client.generate(prompt, system=system_prompt)

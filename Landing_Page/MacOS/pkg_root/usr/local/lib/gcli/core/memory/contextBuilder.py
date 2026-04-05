class ContextBuilder:
    """Formats and injects retrieved context into model prompts."""
    
    def build_prompt_injection(self, recall: dict) -> str:
        """Creates a cohesive string of context to be injected into a system prompt."""
        injection = "### COGNITIVE CONTEXT (RECALLED MEMORY) ###\n"
        
        # Session Memory
        session = recall.get("session", {})
        if session:
            injection += f"Session Status: Continuing from objective '{session.get('last_objective')}'\n"
        
        # Knowledge Context
        knowledge = recall.get("knowledge", [])
        if knowledge:
            injection += "Related Project Knowledge:\n"
            for k in knowledge:
                injection += f"- {k}\n"

        # Reasoning Context
        reasoning = recall.get("reasoning", [])
        if reasoning:
            injection += "Past Engineering Reasoning:\n"
            for r in reasoning:
                injection += f"- {r}\n"
        
        return injection

from models import ModelFactory

class MonetizationEngine:
    """Suggests concrete business models and execution strategies for identified opportunities."""
    def __init__(self, model_type: str = "claude"):
        self.client = ModelFactory.get_client(model_type)

    def suggest_strategy(self, opportunity: str) -> str:
        system_prompt = "You are the Gaia Revenue Strategist. Provide a concrete business model and monetization plan for the given opportunity."
        prompt = f"Opportunity: {opportunity}\n\nDevelop a strategic monetization plan."
        return self.client.generate(prompt, system=system_prompt)

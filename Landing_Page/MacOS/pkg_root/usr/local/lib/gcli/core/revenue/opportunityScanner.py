from agents.researcherAgent import ResearcherAgent

class OpportunityScanner:
    """Uses the Researcher agent to scan contexts and market data for revenue opportunities."""
    def __init__(self):
        self.researcher = ResearcherAgent()

    def scan(self, context: str) -> str:
        task = "Identify 3 potential revenue-generating opportunities within this codebase or context. Focus on automation, micro-products, or efficiency services."
        return self.researcher.act(task, context)

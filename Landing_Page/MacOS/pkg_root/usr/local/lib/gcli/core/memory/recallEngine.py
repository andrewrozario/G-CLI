from memory.vector_db import VectorMemory
from core.gaia.deviceIntegration import DeviceIntegration

class RecallEngine:
    """Intelligently retrieves session-level and long-term context for current tasks."""
    def __init__(self):
        self.vector_memory = VectorMemory()
        self.session_memory = DeviceIntegration()

    def get_context(self, objective: str) -> dict:
        """Collects relevant session and history data."""
        # 1. Active Session Context
        session = self.session_memory.load_session_state()
        
        # 2. Semantic History Recall
        past_knowledge = self.vector_memory.retrieve(objective, n_results=3, collection_name="knowledge")
        past_reasoning = self.vector_memory.retrieve(objective, n_results=3, collection_name="reasoning")
        
        return {
            "session": session,
            "knowledge": past_knowledge,
            "reasoning": past_reasoning
        }

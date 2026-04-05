from abc import ABC, abstractmethod
from router.model_router import ModelRouter
from memory.vector_db import VectorMemory

class BaseAgent(ABC):
    """The fundamental cognitive unit of G CLI v3."""
    
    def __init__(self, name: str, role: str, preferred_model: str = "local"):
        self.name = name
        self.role = role
        self.preferred_model = preferred_model
        self.router = ModelRouter()
        self.memory = VectorMemory()
        self.client = self.router.get_client(preferred_model)

    @abstractmethod
    def act(self, task: str, context: str = "") -> str:
        """The primary action loop for the agent."""
        pass

    def retrieve_memory(self, query: str) -> str:
        return str(self.memory.retrieve(query, n_results=3))

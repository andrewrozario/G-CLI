from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class BaseModelClient(ABC):
    @abstractmethod
    def generate(self, prompt: str, system: str = "", **kwargs) -> str:
        """Generate a response for a given prompt."""
        pass

    @abstractmethod
    def generate_json(self, prompt: str, system: str = "", **kwargs) -> str:
        """Generate a response in JSON format."""
        pass

import json
import os

class RoutingMemory:
    """Stores execution history to enable self-learning routing decisions."""
    def __init__(self, memory_path: str = "core/intelligence/routing_history.json"):
        self.memory_path = memory_path
        self.history = self._load_history()

    def _load_history(self) -> list:
        if os.path.exists(self.memory_path):
            try:
                with open(self.memory_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        return []

    def save_record(self, record: dict):
        self.history.append(record)
        with open(self.memory_path, 'w') as f:
            json.dump(self.history, f, indent=2)

    def get_history(self) -> list:
        return self.history

import json
import os

class DeviceIntegration:
    """Handles continuity of tasks and environment specifics."""
    def __init__(self, memory_path: str = "core/gaia/session_memory.json"):
        self.memory_path = memory_path

    def save_session_state(self, objective: str, last_action: str):
        data = {
            "last_objective": objective,
            "last_action": last_action,
            "timestamp": "current_time" # Simplified
        }
        with open(self.memory_path, 'w') as f:
            json.dump(data, f)

    def load_session_state(self) -> dict:
        if os.path.exists(self.memory_path):
            with open(self.memory_path, 'r') as f:
                return json.load(f)
        return {}

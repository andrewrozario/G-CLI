import json
import os

class DecisionBias:
    """Influences architectural and implementation choices based on core priorities."""
    def __init__(self, profile_path: str = "core/personality/gaiaProfile.json"):
        self.profile_path = profile_path
        self.priorities = self._load_priorities()

    def _load_priorities(self) -> list:
        if os.path.exists(self.profile_path):
            with open(self.profile_path, 'r') as f:
                data = json.load(f)
                return data.get("priorities", [])
        return ["clean code", "stability"]

    def apply_bias(self, plan: list) -> str:
        bias_str = "When executing, prioritize the following principles:\n"
        for p in self.priorities:
            bias_str += f"- {p}\n"
        return bias_str

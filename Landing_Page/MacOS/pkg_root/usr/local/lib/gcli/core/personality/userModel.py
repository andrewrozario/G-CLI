import json
import os

class UserModel:
    """Tracks the user's implicit preferences and current context to align Gaia's behavior."""
    def __init__(self, profile_path: str = "core/personality/gaiaProfile.json"):
        self.profile_path = profile_path
        self.alignment = self._load_alignment()

    def _load_alignment(self) -> dict:
        if os.path.exists(self.profile_path):
            with open(self.profile_path, 'r') as f:
                data = json.load(f)
                return data.get("user_alignment", {})
        return {}

    def get_alignment_string(self) -> str:
        traits = [k for k, v in self.alignment.items() if v]
        return f"Align responses with the following user traits: {', '.join(traits)}."

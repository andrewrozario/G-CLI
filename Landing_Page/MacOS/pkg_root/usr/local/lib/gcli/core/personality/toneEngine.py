import json
import os

class ToneEngine:
    """Injects Gaia's unique identity and style into the system prompts."""
    def __init__(self, profile_path: str = "core/personality/gaiaProfile.json"):
        self.profile_path = profile_path
        self.profile = self._load_profile()

    def _load_profile(self) -> dict:
        if os.path.exists(self.profile_path):
            with open(self.profile_path, 'r') as f:
                return json.load(f)
        return {"name": "Gaia", "style": "professional"}

    def apply_tone(self, base_prompt: str) -> str:
        name = self.profile.get("name", "Gaia")
        style = self.profile.get("style", "intelligent")
        tone_instruction = f"You are {name}. Maintain a {style} tone."
        return f"{tone_instruction}\n\n{base_prompt}"

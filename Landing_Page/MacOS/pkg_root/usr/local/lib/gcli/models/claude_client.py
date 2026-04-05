import os
import anthropic
import json
from .base_client import BaseModelClient

class ClaudeClient(BaseModelClient):
    """Client for Anthropic's Claude models."""
    def __init__(self, model_name: str = 'claude-3-5-sonnet-20240620', api_key: str = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)
            self.model_name = model_name
        else:
            self.client = None

    def generate(self, prompt: str, system: str = "", **kwargs) -> str:
        if not self.client:
            return "Error: ANTHROPIC_API_KEY not found."
        
        try:
            message = self.client.messages.create(
                model=self.model_name,
                max_tokens=4096,
                system=system,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            return f"Error with Claude ({self.model_name}): {str(e)}"

    def generate_json(self, prompt: str, system: str = "", **kwargs) -> str:
        if not self.client:
            return json.dumps({"error": "ANTHROPIC_API_KEY not found."})
        
        # Ensure system prompt asks for JSON
        system_with_json = f"{system}\n\nRespond ONLY in valid JSON format." if system else "Respond ONLY in valid JSON format."
        
        try:
            message = self.client.messages.create(
                model=self.model_name,
                max_tokens=4096,
                system=system_with_json,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            return json.dumps({"error": f"Error with Claude ({self.model_name}): {str(e)}"})

import os
import openai
import json
from .base_client import BaseModelClient

class CodexClient(BaseModelClient):
    """Client for OpenAI's coding models (GPT-4o)."""
    def __init__(self, model_name: str = 'gpt-4o', api_key: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if self.api_key:
            self.client = openai.OpenAI(api_key=self.api_key)
            self.model_name = model_name
        else:
            self.client = None

    def generate(self, prompt: str, system: str = "", **kwargs) -> str:
        if not self.client:
            return "Error: OPENAI_API_KEY not found."
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error with Codex/OpenAI ({self.model_name}): {str(e)}"

    def generate_json(self, prompt: str, system: str = "", **kwargs) -> str:
        if not self.client:
            return json.dumps({"error": "OPENAI_API_KEY not found."})
        
        messages = []
        # Ensure system prompt asks for JSON
        system_with_json = f"{system}\n\nRespond ONLY in valid JSON format." if system else "Respond ONLY in valid JSON format."
        messages.append({"role": "system", "content": system_with_json})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                response_format={"type": "json_object"}
            )
            return response.choices[0].message.content
        except Exception as e:
            return json.dumps({"error": f"Error with Codex/OpenAI ({self.model_name}): {str(e)}"})

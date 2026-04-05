import os
import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import google.generativeai as genai
import json
from .base_client import BaseModelClient

class GeminiClient(BaseModelClient):
    """Client for Google's Gemini Pro models."""
    def __init__(self, model_name: str = 'gemini-1.5-pro', api_key: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            # Use the exact model identifier for Pro
            self.model_name = 'gemini-1.5-pro'
            self.model = genai.GenerativeModel(self.model_name)
        else:
            self.model = None

    def generate(self, prompt: str, system: str = "", **kwargs) -> str:
        if not self.model:
            return "Error: GEMINI_API_KEY not found."
        
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        try:
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            return f"Error with Gemini Pro ({self.model_name}): {str(e)}"

    def generate_json(self, prompt: str, system: str = "", **kwargs) -> str:
        if not self.model:
            return json.dumps({"error": "GEMINI_API_KEY not found."})
        
        if "JSON" not in system.upper() and "JSON" not in prompt.upper():
            prompt += "\n\nRespond ONLY in valid JSON format."
            
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        try:
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json"
                )
            )
            return response.text
        except Exception as e:
            return json.dumps({"error": f"Error with Gemini Pro ({self.model_name}): {str(e)}"})

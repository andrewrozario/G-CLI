import os
import google.generativeai as genai

class GeminiFrontierBridge:
    """Provides Gaia with access to Gemini's frontier reasoning capabilities."""
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro')
        else:
            self.model = None

    def ask_frontier(self, prompt: str) -> str:
        if not self.model:
            return "Error: GEMINI_API_KEY not found. Frontier boost disabled."
        
        response = self.model.generate_content(prompt)
        return response.text

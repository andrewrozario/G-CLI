import json
import requests
import logging
import os
from typing import List, Dict, Any, Optional
from gaia_cmd.core.llm.provider import LLMProvider
from gaia_cmd.core.llm.state import get_model

class LocalOllamaProvider(LLMProvider):
    """
    Real implementation of Ollama local LLM provider.
    Synchronized with system-wide model state.
    """
    def __init__(self, model_name: str = None, base_url: str = None):
        super().__init__("Ollama", model_name or get_model())
        self.base_url = base_url or os.getenv("OLLAMA_API_BASE", "http://localhost:11434")
        self.generate_url = f"{self.base_url}/api/generate"

    def test_connection(self) -> bool:
        """Verifies if Ollama server is reachable."""
        try:
            response = requests.get(self.base_url, timeout=5)
            return response.status_code == 200
        except:
            return False

    def generate(self, prompt: Any, **kwargs) -> Dict[str, Any]:
        """
        Sends a request to local Ollama instance using the synchronized system model.
        """
        # Always use the global state model unless specifically overridden in kwargs
        model_name = kwargs.get("model") or get_model()
        
        if not self.test_connection():
            raise RuntimeError(f"Ollama server unreachable at {self.base_url}")

        print(f"[MODEL] {model_name}")
        
        if isinstance(prompt, list):
            full_prompt = ""
            for msg in prompt:
                full_prompt += f"{msg['role'].upper()}: {msg['content']}\n"
            full_prompt += "ASSISTANT: "
        else:
            full_prompt = prompt

        payload = {
            "model": model_name,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", 0.2)
            }
        }

        try:
            response = requests.post(self.generate_url, json=payload, timeout=120)
            if response.status_code != 200:
                raise Exception(f"Ollama error: {response.text}")
            
            data = response.json()
            return {
                "content": data.get("response", ""),
                "tool_calls": [],
                "model": model_name,
                "provider": "ollama"
            }
        except Exception as e:
            raise RuntimeError(f"Ollama request failed: {e}")

    def stream(self, messages: Any):
        pass

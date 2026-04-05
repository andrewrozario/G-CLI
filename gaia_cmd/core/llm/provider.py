import abc
import logging
import google.generativeai as genai
from typing import List, Dict, Any, Optional
from gaia_cmd.core.llm.state import get_model

class LLMProvider(abc.ABC):
    """
    Abstract Base Class for all LLM Providers.
    """
    def __init__(self, provider_name: str, model_name: str):
        self.provider_name = provider_name
        self.model_name = model_name
        self.logger = logging.getLogger(f"LLM.{self.provider_name}")

    @abc.abstractmethod
    def generate(self, prompt: Any, **kwargs) -> Dict[str, Any]:
        """
        Generates a completion from the LLM.
        """
        pass

class OllamaProvider(LLMProvider):
    def __init__(self, model_name: str = None, base_url: str = "http://localhost:11434"):
        super().__init__("Ollama", model_name or get_model())
        self.base_url = base_url

    def generate(self, prompt: Any, **kwargs) -> Dict[str, Any]:
        model_name = kwargs.get("model") or get_model()
        self.logger.info(f"Generating completion with model {model_name}")
        return {"content": "[Ollama] Reasoning through task...", "tool_calls": []}

class GeminiProvider(LLMProvider):
    """
    Official Google Gemini API Provider.
    Supports gemini-1.5-pro and gemini-1.5-flash.
    """
    def __init__(self, api_key: str, model_name: str = None):
        super().__init__("Gemini", model_name or "gemini-1.5-pro")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(self.model_name)

    def generate(self, prompt: Any, **kwargs) -> Dict[str, Any]:
        model_name = kwargs.get("model") or self.model_name
        self.logger.info(f"Connecting to Google AI (Gemini) using model {model_name}")
        
        try:
            # Handle messages list vs single prompt
            if isinstance(prompt, list):
                contents = []
                for msg in prompt:
                    role = "user" if msg["role"] == "user" else "model"
                    contents.append({"role": role, "parts": [msg["content"]]})
                response = self.model.generate_content(contents)
            else:
                response = self.model.generate_content(str(prompt))
            
            return {
                "content": response.text,
                "tool_calls": [],
                "model": model_name,
                "provider": "gemini"
            }
        except Exception as e:
            self.logger.error(f"Gemini API failure: {e}")
            raise RuntimeError(f"Gemini API error: {str(e)}")

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model_name: str = None):
        super().__init__("OpenAI", model_name or "gpt-4o")
        self.api_key = api_key

    def generate(self, prompt: Any, **kwargs) -> Dict[str, Any]:
        model_name = kwargs.get("model") or self.model_name
        self.logger.info(f"Generating completion with model {model_name}")
        return {"content": "[OpenAI] Optimized logic analysis...", "tool_calls": []}

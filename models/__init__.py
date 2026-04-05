from .claude_client import ClaudeClient
from .gemini_client import GeminiClient
from .codex_client import CodexClient
from .base_client import BaseModelClient
import json

class ModelFactory:
    @staticmethod
    def get_client(model_type: str, model_name: str = None) -> BaseModelClient:
        if model_type == "claude":
            return ClaudeClient(model_name=model_name or 'claude-3-5-sonnet-20240620')
        elif model_type == "gemini":
            return GeminiClient(model_name=model_name or 'gemini-1.5-pro')
        elif model_type == "codex":
            return CodexClient(model_name=model_name or 'gpt-4o')
        else:
            # Pro cloud fallback
            return GeminiClient(model_name='gemini-1.5-pro')

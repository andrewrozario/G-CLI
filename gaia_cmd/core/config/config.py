import os
import json
import logging
from typing import Dict, Any, Optional

class GaiaConfig:
    """
    Manages Gaia CLI configuration including model settings, API keys,
    GitHub tokens, and routing rules.
    """
    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root
        self.config_dir = os.path.join(workspace_root, "config")
        self.config_file = os.path.join(self.config_dir, "settings.json")
        self.logger = logging.getLogger("GaiaConfig")
        
        self._ensure_config()
        self.settings = self._load_config()

    def _ensure_config(self):
        os.makedirs(self.config_dir, exist_ok=True)
        if not os.path.exists(self.config_file):
            default_settings = {
                "llm": {
                    "default_provider": "ollama",
                    "providers": {
                        "ollama": {
                            "model": "llama3:8b",
                            "base_url": "http://localhost:11434"
                        },
                        "gemini": {
                            "model": "gemini-1.5-pro",
                            "api_key": os.getenv("GEMINI_API_KEY", "")
                        },
                        "openai": {
                            "model": "gpt-4o",
                            "api_key": os.getenv("OPENAI_API_KEY", "")
                        }
                    },
                    "routing_rules": {
                        "simple": "ollama",
                        "complex": "gemini",
                        "architecture": "gemini",
                        "debugging": "ollama",
                        "coding": "ollama"
                    }
                },
                "integrations": {
                    "github": {
                        "token": os.getenv("GITHUB_TOKEN", ""),
                        "username": os.getenv("GITHUB_USERNAME", ""),
                        "default_visibility": "public"
                    },
                    "package_managers": {
                        "npm": {"registry": "https://registry.npmjs.org/"},
                        "pip": {"index_url": "https://pypi.org/simple"}
                    }
                }
            }
            with open(self.config_file, "w") as f:
                json.dump(default_settings, f, indent=4)

    def _load_config(self) -> Dict[str, Any]:
        try:
            with open(self.config_file, "r") as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            return {}

    def get_provider_settings(self, provider_name: str) -> Dict[str, Any]:
        return self.settings.get("llm", {}).get("providers", {}).get(provider_name, {})

    def get_routing_rule(self, task_type: str) -> str:
        return self.settings.get("llm", {}).get("routing_rules", {}).get(task_type, "ollama")

    def get_default_provider(self) -> str:
        return self.settings.get("llm", {}).get("default_provider", "ollama")

    def get_integration_settings(self, integration_name: str) -> Dict[str, Any]:
        return self.settings.get("integrations", {}).get(integration_name, {})

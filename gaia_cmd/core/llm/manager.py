import logging
from typing import List, Dict, Any, Optional
from gaia_cmd.core.llm.provider import LLMProvider, GeminiProvider, OpenAIProvider
from gaia_cmd.core.llm.local_provider import LocalOllamaProvider
from gaia_cmd.core.llm.router import ModelRouter, TaskComplexity
from gaia_cmd.core.config.config import GaiaConfig
from gaia_cmd.core.llm.safe_generate import safe_generate

class LLMManager(LLMProvider):
    """
    Orchestrates multiple LLM providers.
    Handles dynamic routing based on task complexity and fallback logic.
    Implements LLMProvider interface for seamless integration.
    """
    def __init__(self, config: GaiaConfig):
        super().__init__("Manager", "Dynamic")
        self.config = config
        self.logger = logging.getLogger("LLMManager")
        self.providers: Dict[str, LLMProvider] = {}
        self.forced_provider: Optional[str] = None
        self.router = ModelRouter()
        self._initialize_providers()

    def _initialize_providers(self):
        """Pre-warms all configured providers."""
        for provider_name in ["ollama", "gemini", "openai"]:
            settings = self.config.get_provider_settings(provider_name)
            if provider_name == "ollama":
                self.providers[provider_name] = LocalOllamaProvider(
                    model_name=settings.get("model", "qwen2.5-coder:7b"),
                    base_url=settings.get("base_url", "http://localhost:11434")
                )
            elif provider_name == "gemini" and settings.get("api_key"):
                self.providers[provider_name] = GeminiProvider(
                    api_key=settings["api_key"],
                    model_name=settings.get("model", "gemini-1.5-pro")
                )
            elif provider_name == "openai" and settings.get("api_key"):
                self.providers[provider_name] = OpenAIProvider(
                    api_key=settings["api_key"],
                    model_name=settings.get("model", "gpt-4o")
                )

    def set_forced_provider(self, provider_name: str):
        """Forces the manager to use a specific provider (e.g. from CLI flag)."""
        if provider_name in ["ollama", "local"]:
            self.forced_provider = "ollama"
        elif provider_name in self.providers:
            self.forced_provider = provider_name
        else:
            self.logger.warning(f"Requested provider {provider_name} not available. Ignoring.")

    def generate(self, prompt: Any, **kwargs) -> Dict[str, Any]:
        """
        Routes the request based on task complexity.
        Implements fallback if the primary model fails.
        Standardized interface: generate(prompt, **kwargs)
        """
        task_description = kwargs.get("task_description", "")
        
        # 1. Evaluate complexity and get route
        route = self.router.get_route(task_description)
        primary_provider_name = route["primary"]
        fallback_order = route["fallback"]
        
        # 2. Handle Forced Provider (CLI flag overrides routing)
        if self.forced_provider:
            primary_provider_name = self.forced_provider
            if primary_provider_name in fallback_order:
                fallback_order.remove(primary_provider_name)
            fallback_order.insert(0, primary_provider_name)
        else:
            if primary_provider_name in fallback_order:
                fallback_order.remove(primary_provider_name)
            fallback_order.insert(0, primary_provider_name)

        self.logger.info(f"Routing task | Complexity: {route['complexity']} | Target: {primary_provider_name}")

        # 3. Execution with Fallback
        last_error = None
        for provider_name in fallback_order:
            provider = self.providers.get(provider_name)
            if not provider:
                continue

            try:
                self.logger.info(f"Attempting completion with {provider_name}...")
                # Pass prompt and all keyword arguments to the provider via safe wrapper
                result = safe_generate(provider, prompt, **kwargs)
                
                # Add routing metadata
                result["routing"] = {
                    "complexity": route["complexity"],
                    "used_provider": provider_name,
                    "refinement_applied": route["refinement_required"]
                }
                
                return result
            except Exception as e:
                self.logger.warning(f"Provider {provider_name} failed: {e}. Trying fallback...")
                last_error = e

        self.logger.error("All LLM providers in route failed.")
        raise RuntimeError(f"All LLM providers failed. Last error: {last_error}")

    def get_available_providers(self) -> List[str]:
        return list(self.providers.keys())

import logging

logger = logging.getLogger("SafeGenerate")

def safe_generate(provider, prompt, **kwargs):
    """
    Wraps LLM provider calls to prevent crashes from argument mismatches.
    Falls back to a basic call if extended keyword arguments are rejected.
    """
    try:
        return provider.generate(prompt, **kwargs)
    except TypeError as e:
        logger.warning(f"Provider {provider.provider_name} rejected extended arguments: {e}. Falling back to basic prompt.")
        # If the provider is an instance of LLMProvider, it might have a different signature.
        # We try to pass only the prompt if the detailed one fails.
        return provider.generate(prompt)

import os

# Centralized Model Identity Substrate
DEFAULT_MODEL = os.getenv("GAIA_DEFAULT_MODEL", "qwen2.5-coder:7b")
FALLBACK_MODEL = "mistral"

# UI Display Name Mapping
MODEL_DISPLAY_NAMES = {
    "qwen2.5-coder:7b": "DeepSeek Code", # Or actual Qwen name
    "gemini-1.5-pro": "Gemini 1.5 Pro",
    "gpt-4o": "OpenAI GPT-4o"
}

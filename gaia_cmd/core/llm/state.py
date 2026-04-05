import os

# Single Source of Truth for Model Identity
# This state is shared across the UI and all LLM Providers
current_model = os.getenv("GAIA_MODEL", "qwen2.5-coder:7b")

def set_model(model_name: str):
    global current_model
    current_model = model_name
    print(f"[MODEL] Synchronized to: {current_model}")

def get_model() -> str:
    return current_model

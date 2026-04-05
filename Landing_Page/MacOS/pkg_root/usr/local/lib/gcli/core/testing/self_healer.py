from models import ModelFactory

class SelfHealer:
    """Uses Codex to generate surgical fixes for specific test failures."""
    def __init__(self):
        self.client = ModelFactory.get_client("codex")

    def fix(self, errors: list, file_content: str, file_path: str) -> str:
        error_str = "\n".join(errors)
        system_prompt = "You are a senior engineer. Fix the provided errors in the code. Return ONLY the FULL FIXED CODE block with the header 'FILE_WRITE:path/to/file'."
        prompt = f"FILE: {file_path}\nERRORS:\n{error_str}\n\nCURRENT CODE:\n{file_content}\n\nFix the errors and return the corrected code."
        
        return self.client.generate(prompt, system=system_prompt)

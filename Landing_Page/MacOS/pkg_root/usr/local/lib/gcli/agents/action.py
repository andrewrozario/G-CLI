import os
import difflib
from core.llm_client import LocalLLMClient
from core.prompts import build_system_prompt

class ActionSystem:
    """Enables Gaia to propose and apply code transformations safely."""
    
    def __init__(self, llm: LocalLLMClient):
        self.llm = llm

    def suggest_refactor(self, file_path: str, objective: str) -> str:
        if not os.path.exists(file_path):
            return "File not found."
            
        with open(file_path, 'r') as f:
            original_code = f.read()
            
        prompt = f"Objective: {objective}\nFile: {file_path}\nOriginal Code:\n{original_code}\n\nSuggest a refactored version of this code. Output ONLY the new code block."
        new_code = self.llm.generate(prompt, system=build_system_prompt("software_architect", "chain_of_thought"))
        
        # Simple heuristic to clean output code block if model adds markdown
        new_code = new_code.strip()
        if "```" in new_code:
            lines = new_code.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].startswith("```"):
                lines = lines[:-1]
            new_code = "\n".join(lines).strip()

        return new_code

    def preview_diff(self, original_path: str, new_code: str) -> str:
        with open(original_path, 'r') as f:
            old_code = f.read().splitlines()
            
        new_code_lines = new_code.splitlines()
        
        diff = difflib.unified_diff(
            old_code, new_code_lines, 
            fromfile=original_path, tofile=original_path + " (refactored)"
        )
        return "\n".join(list(diff))

    def apply_patch(self, file_path: str, new_code: str):
        # Always create a backup first
        backup_path = file_path + ".gaia_backup"
        os.rename(file_path, backup_path)
        
        with open(file_path, 'w') as f:
            f.write(new_code)
        
        return f"Successfully applied changes. Backup saved to {backup_path}"

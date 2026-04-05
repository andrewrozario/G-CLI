import os
import json
import logging
import time
from typing import Dict, Any, List, Optional
from gaia_cmd.core.debugging.classifier import ErrorCategory

class KnownFixesDatabase:
    """
    Persistently stores successful fixes mapped to specific error signatures.
    Allows Gaia to instantly fix previously solved bugs.
    """
    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root
        self.logger = logging.getLogger("KnownFixesDatabase")
        self.db_file = os.path.join(workspace_root, "memory", "debugging", "known_fixes.json")
        self._ensure_db()
        self.fixes = self._load()

    def _ensure_db(self):
        os.makedirs(os.path.dirname(self.db_file), exist_ok=True)
        if not os.path.exists(self.db_file):
            with open(self.db_file, "w") as f:
                json.dump([], f)

    def _load(self) -> List[Dict[str, Any]]:
        try:
            with open(self.db_file, "r") as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load known fixes DB: {e}")
            return []

    def _save(self):
        try:
            # Keep DB size manageable
            if len(self.fixes) > 500:
                self.fixes = self.fixes[-500:]
            with open(self.db_file, "w") as f:
                json.dump(self.fixes, f, indent=4)
        except Exception as e:
            self.logger.error(f"Failed to save known fixes DB: {e}")

    def add_fix(self, error_text: str, category: ErrorCategory, fix_description: str, task_context: str):
        """Records a successful fix for future reference."""
        # Create a simplified 'signature' of the error to match against later
        # (e.g. taking the last 3 lines or key exception text)
        lines = [line.strip() for line in error_text.split('\n') if line.strip()]
        signature = "\n".join(lines[-2:]) if len(lines) >= 2 else error_text

        entry = {
            "timestamp": time.time(),
            "category": category.value,
            "error_signature": signature,
            "fix_description": fix_description,
            "context": task_context
        }
        self.fixes.append(entry)
        self._save()
        self.logger.info(f"Recorded known fix for category: {category.value}")

    def find_potential_fix(self, error_text: str) -> Optional[str]:
        """
        Searches the database for a similar error signature.
        Returns the fix description if found.
        """
        # Very basic signature matching (substring)
        lines = [line.strip() for line in error_text.split('\n') if line.strip()]
        signature = "\n".join(lines[-2:]) if len(lines) >= 2 else error_text
        
        for fix in reversed(self.fixes): # Search newest first
            if fix["error_signature"] in signature or signature in fix["error_signature"]:
                self.logger.info("Found known fix in database.")
                return fix["fix_description"]
                
        return None

import logging
from typing import Dict, Any, Optional
from gaia_cmd.core.llm.provider import LLMProvider
from gaia_cmd.core.llm.safe_generate import safe_generate
from gaia_cmd.core.debugging.classifier import ErrorClassifier, ErrorCategory
from gaia_cmd.core.debugging.database import KnownFixesDatabase
from gaia_cmd.core.execution.error_parser import ErrorParser

class DebugEngine:
    """
    Advanced autonomous debugging system.
    Classifies errors, checks known fixes, and generates dynamic patches.
    """
    def __init__(self, workspace_root: str, llm: LLMProvider):
        self.workspace_root = workspace_root
        self.llm = llm
        self.logger = logging.getLogger("DebugEngine")
        self.classifier = ErrorClassifier()
        self.db = KnownFixesDatabase(workspace_root)
        self.error_parser = ErrorParser()

    def analyze_and_suggest_fix(self, raw_error: str, context_task: str) -> str:
        """
        Takes raw stderr, parses it, categorizes it, and returns a concrete fix strategy.
        """
        # 1. Clean the noise
        clean_error_data = self.error_parser.parse(raw_error)
        clean_error = clean_error_data.get("message", "")
        
        if not clean_error:
            return "No readable error output provided."

        self.logger.info(f"Analyzing error: {clean_error[:50]}...")

        # 2. Classify
        category = self.classifier.classify(clean_error)
        location = self.classifier.extract_file_and_line(clean_error)
        self.logger.debug(f"Categorized as: {category.value} at {location}")

        # 3. Check Known Fixes Database
        known_fix = self.db.find_potential_fix(clean_error)
        if known_fix:
            self.logger.info("Using previously learned fix.")
            return f"Known Fix ([{category.value}]): {known_fix}"

        # 4. Generate dynamic fix via LLM
        dynamic_fix = self._generate_dynamic_fix(category, clean_error, location, context_task)
        
        return f"Dynamic Fix ([{category.value}] at {location['file']}:{location['line']}): {dynamic_fix}"

    def record_successful_fix(self, raw_error: str, fix_applied: str, context_task: str):
        """
        Called by the orchestrator when a retry succeeds, so the engine learns.
        """
        clean_error_data = self.error_parser.parse(raw_error)
        clean_error = clean_error_data.get("message", "")
        
        category = self.classifier.classify(clean_error)
        self.db.add_fix(clean_error, category, fix_applied, context_task)

    def _generate_dynamic_fix(self, category: ErrorCategory, error_text: str, location: Dict[str, str], context_task: str) -> str:
        """Generates a concrete fix strategy using LLM."""
        system_prompt = (
            "You are the Gaia CLI Debugging Expert. Your goal is to provide a specific, "
            "actionable fix for the provided error. Consider the error category and location."
        )
        
        user_prompt = (
            f"ERROR CATEGORY: {category.value}\n"
            f"ERROR TEXT: {error_text}\n"
            f"LOCATION: {location}\n"
            f"TASK CONTEXT: {context_task}\n\n"
            "Provide a concise fix strategy (max 3 sentences)."
        )
        
        try:
            response_data = safe_generate(self.llm, [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ], task_description=f"Fixing error in: {context_task}")
            return response_data.get("content", "").strip()
        except Exception as e:
            self.logger.error(f"LLM Debugging failed: {e}")
            # Fallback to rule-based logic
            if category == ErrorCategory.IMPORT:
                return f"Check requirements.txt/package.json and run install command. Ensure path '{location['file']}' is correct."
            elif category == ErrorCategory.SYNTAX:
                return f"Open {location['file']} at line {location['line']} and fix syntax."
            return "Read the file mentioned in the stack trace and look for logical errors."

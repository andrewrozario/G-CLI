import logging
from typing import Any, Dict, Optional
from gaia_cmd.core.llm.provider import LLMProvider
from gaia_cmd.core.execution.error_parser import ErrorParser

class ErrorAnalyzer:
    """
    Analyzes execution failures (e.g., test failures, build errors)
    and provides structured feedback to the Coder agent.
    """
    def __init__(self, llm: LLMProvider):
        self.llm = llm
        self.logger = logging.getLogger("ErrorAnalyzer")

    def analyze(self, error_output: str, last_action: Dict[str, Any]) -> str:
        """
        Analyzes the error and returns a human-readable diagnosis and suggestion.
        First parses the raw error to remove noise, then analyzes the core issue.
        """
        self.logger.info("Analyzing error output...")
        
        # 1. Parse raw stderr to get the actual traceback/error message
        parser = ErrorParser()
        clean_error_data = parser.parse(error_output)
        clean_error = clean_error_data.get("message", "")
        
        system_prompt = (
            "You are the Gaia CLI Error Expert. Your job is to analyze build/test errors "
            "and identify the root cause. Suggest a fix for the Coder agent."
        )
        
        # In a real scenario, this would be another LLM call to get specialized diagnosis.
        # For the demo, we mock the analysis but log the clean error to show it works.
        self.logger.debug(f"Cleaned Error Input: {clean_error}")
        
        # Simple rule-based mock for demonstration:
        if "ImportError" in clean_error:
            return "Diagnosis: Missing module. Suggestion: Install the missing dependency."
        elif "AssertionError" in clean_error:
            return "Diagnosis: Logic error in test validation. Suggestion: Review the expected vs actual values."
        elif "SyntaxError" in clean_error:
            return "Diagnosis: Syntax Error in recent code changes. Suggestion: Fix missing colons, brackets, or indentation."
        else:
            return f"Diagnosis: Execution failure detected. Root issue: {clean_error[:100]}... Suggestion: Check recent file changes."

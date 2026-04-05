class ErrorParser:
    """
    Analyzes raw error output to extract type, message, and suggested fixes.
    """
    def parse(self, error_output: str) -> dict:
        return {
            "type": self.detect_type(error_output),
            "message": error_output,
            "suggestion": self.suggest_fix(error_output)
        }

    def detect_type(self, error_output: str) -> str:
        if "ModuleNotFoundError" in error_output:
            return "MISSING_MODULE"
        if "ImportError" in error_output:
            return "IMPORT_ERROR"
        if "SyntaxError" in error_output:
            return "SYNTAX_ERROR"
        return "UNKNOWN"

    def suggest_fix(self, error_output: str) -> str:
        if "ModuleNotFoundError" in error_output:
            return "Check dependencies or install missing package"
        if "ImportError" in error_output:
            return "Verify import paths"
        if "SyntaxError" in error_output:
            return "Check code syntax"
        return "Inspect logs"

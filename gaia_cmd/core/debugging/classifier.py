import re
from enum import Enum
from typing import Dict, Any

class ErrorCategory(Enum):
    SYNTAX = "Syntax Error"
    IMPORT = "Import/Dependency Error"
    RUNTIME = "Runtime Exception"
    ASSERTION = "Test/Assertion Failure"
    BUILD = "Build/Compilation Error"
    UNKNOWN = "Unknown Error"

class ErrorClassifier:
    """
    Analyzes raw error text and categorizes it using regex heuristics.
    """
    @staticmethod
    def classify(error_text: str) -> ErrorCategory:
        text = error_text.lower()
        
        # Syntax Errors
        if re.search(r"syntaxerror|unexpected token|expected.*but got|indentationerror", text):
            return ErrorCategory.SYNTAX
            
        # Import Errors
        if re.search(r"importerror|modulenotfounderror|cannot find module|err_module_not_found", text):
            return ErrorCategory.IMPORT
            
        # Assertion / Test Errors
        if re.search(r"assertionerror|expected.*to be|failed test", text):
            return ErrorCategory.ASSERTION
            
        # Build / Compilation
        if re.search(r"compilation failed|build error|tsc|npm err! code elifecycle", text):
            return ErrorCategory.BUILD
            
        # Generic Runtime (Type, Value, Name, Reference)
        if re.search(r"typeerror|valueerror|nameerror|referenceerror|attributeerror", text):
            return ErrorCategory.RUNTIME

        return ErrorCategory.UNKNOWN

    @staticmethod
    def extract_file_and_line(error_text: str) -> Dict[str, str]:
        """Attempts to extract the specific file and line number from the error."""
        # Python traceback style
        py_match = re.search(r'File "([^"]+)", line (\d+)', error_text)
        if py_match:
            return {"file": py_match.group(1), "line": py_match.group(2)}
            
        # Node/JS style
        js_match = re.search(r'at .* \(([^:]+):(\d+):\d+\)', error_text)
        if js_match:
            return {"file": js_match.group(1), "line": js_match.group(2)}
            
        return {"file": "unknown", "line": "unknown"}

import re

class ErrorParser:
    """Extracts high-signal error messages and stack traces from test output."""
    def parse(self, output: str) -> list:
        errors = []
        
        # Look for typical error markers
        patterns = [
            r"ERROR: (.*)",
            r"AssertionError: (.*)",
            r"SyntaxError: (.*)",
            r"ImportError: (.*)",
            r"TypeError: (.*)",
            r"FAILED (.*)"
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, output)
            errors.extend(matches)
            
        if not errors and "Error" in output:
            # Fallback: capture last 10 lines of output if keyword 'Error' is present
            errors = output.splitlines()[-10:]
            
        return errors

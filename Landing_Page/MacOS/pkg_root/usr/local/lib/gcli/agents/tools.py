import os
import ast
import subprocess

class CodingTools:
    """A suite of advanced coding capabilities for Gaia."""
    
    @staticmethod
    def check_python_syntax(code: str) -> str:
        """Validate Python code structure before saving/executing."""
        try:
            ast.parse(code)
            return "Syntax is valid."
        except SyntaxError as e:
            return f"SyntaxError: {e}"

    @staticmethod
    def run_tests(test_command: str) -> str:
        """Execute automated tests and capture results."""
        try:
            result = subprocess.run(
                test_command, shell=True, check=True, 
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            return f"Tests Passed:\n{result.stdout}"
        except subprocess.CalledProcessError as e:
            return f"Tests Failed:\n{e.stderr}\n{e.stdout}"
            
    @staticmethod
    def git_commit(message: str) -> str:
        """Version control integration for safe checkpoints."""
        try:
            subprocess.run("git add .", shell=True, check=True)
            subprocess.run(f"git commit -m '{message}'", shell=True, check=True)
            return "Successfully committed changes."
        except subprocess.CalledProcessError as e:
            return f"Failed to commit: {e}"

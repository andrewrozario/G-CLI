import os
import subprocess
from system.command_runner import CommandRunner

class TestRunner:
    """Detects and executes the appropriate test suite for the project."""
    def __init__(self):
        self.runner = CommandRunner()

    def run(self) -> dict:
        # 1. Detection
        test_cmd = None
        if os.path.exists("pytest.ini") or os.path.exists("tests") or any(f.endswith(".py") for f in os.listdir(".")):
            test_cmd = "pytest"
        elif os.path.exists("package.json"):
            test_cmd = "npm test"
        
        if not test_cmd:
            return {"success": True, "output": "No tests detected. Assuming stability."}

        # 2. Execution
        print(f"🧪 [bold yellow]Running tests ({test_cmd})...[/bold yellow]")
        result = self.runner.run(test_cmd)
        return result

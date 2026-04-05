import subprocess
import os

class CommandRunner:
    """Executes shell commands and handles git operations."""
    
    def run(self, command: str, cwd: str = None) -> dict:
        try:
            result = subprocess.run(
                command, shell=True, check=False, 
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                text=True, cwd=cwd
            )
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode,
                "success": result.returncode == 0
            }
        except Exception as e:
            return {
                "stdout": "",
                "stderr": str(e),
                "exit_code": -1,
                "success": False
            }

    def git_commit(self, message: str) -> str:
        res = self.run(f"git commit -am '{message}'")
        return "Committed successfully." if res["success"] else f"Git commit failed: {res['stderr']}"

    def run_tests(self, test_cmd: str) -> str:
        res = self.run(test_cmd)
        return res["stdout"] if res["success"] else f"Tests Failed:\n{res['stderr']}\n{res['stdout']}"

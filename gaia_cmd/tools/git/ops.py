import subprocess
from typing import Any, Dict
from gaia_cmd.core.tools.base import BaseTool

class GitTool(BaseTool):
    name = "git_ops"
    description = "Executes safe git operations. Use to track changes, diff against HEAD, or rollback."
    parameters_schema = {
        "type": "object",
        "properties": {
            "operation": {
                "type": "string", 
                "enum": ["status", "diff", "commit", "rollback"], 
                "description": "The git operation to perform."
            },
            "message": {
                "type": "string", 
                "description": "Commit message (required for 'commit' operation)."
            }
        },
        "required": ["operation"]
    }

    def __init__(self, workspace_root: str):
        super().__init__()
        self.workspace_root = workspace_root

    def _run(self, operation: str, message: str = "") -> str:
        if operation == "status":
            cmd = "git status"
        elif operation == "diff":
            cmd = "git diff"
        elif operation == "commit":
            if not message:
                raise ValueError("Commit message is required for operation 'commit'")
            # Safe commit: Stages all tracked changes and commits
            cmd = f"git add -u && git commit -m '{message}'"
        elif operation == "rollback":
            # Caution: Hard reset. Good for agent self-correction if tests fail badly
            cmd = "git reset --hard HEAD && git clean -fd"
        else:
            raise ValueError(f"Unsupported git operation: {operation}")

        result = subprocess.run(
            cmd, shell=True, cwd=self.workspace_root, capture_output=True, text=True
        )
        
        if result.returncode != 0 and "nothing to commit" not in result.stdout:
            raise RuntimeError(f"Git command failed: {result.stderr}")
            
        return result.stdout or "Command executed successfully with no output."

import os
from typing import Any, Dict
from gaia_cmd.core.tools.base import BaseTool
from gaia_cmd.core.execution.engine import SafeExecutionEngine

class ShellCommandTool(BaseTool):
    name = "run_shell_command"
    description = "Executes a bash command safely. Use for running tests, starting builds, or executing code. Captures stdout/stderr and prevents infinite loops."
    parameters_schema = {
        "type": "object",
        "properties": {
            "command": {"type": "string", "description": "The shell command to execute."},
            "timeout": {"type": "integer", "description": "Optional timeout in seconds. Defaults to 60."}
        },
        "required": ["command"]
    }

    def __init__(self, workspace_root: str):
        super().__init__()
        self.workspace_root = workspace_root
        # Initialize the new safe execution engine
        # In a real setup, `use_docker` could be read from a config file.
        self.engine = SafeExecutionEngine(workspace_root, use_docker=False)
        
        # Simple Permission Control / Safe Execution Layer
        self.blocked_keywords = ["rm -rf /", "mkfs", "dd if=", ":(){ :|:& };:", "> /dev/sda"]

    def _is_safe(self, command: str) -> bool:
        """Checks command against a blacklist of destructive actions."""
        for blocked in self.blocked_keywords:
            if blocked in command:
                return False
        return True

    def _run(self, command: str, timeout: int = 60) -> Dict[str, Any]:
        if not self._is_safe(command):
            raise PermissionError(f"Command blocked by security policy: {command}")
            
        self.logger.info(f"Executing shell command: {command}")
        
        # Delegate to the execution engine
        result = self.engine.execute(command, timeout=timeout)
        
        if result.timeout_expired:
            raise RuntimeError(f"Command timed out after {timeout} seconds: {command}")
            
        if not result.success:
            # We don't raise an exception here because failed tests (exit code 1)
            # are expected behavior during the agent loop. We just return the error.
            self.logger.warning(f"Command returned non-zero exit code: {result.exit_code}")
        
        return result.to_dict()

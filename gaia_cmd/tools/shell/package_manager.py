import os
import subprocess
import logging
from typing import Any, Dict
from gaia_cmd.core.tools.base import BaseTool

class PackageManagerTool(BaseTool):
    """
    Unified package management tool for Gaia CLI.
    Handles 'npm' and 'pip' operations.
    """
    name = "package_manager"
    description = "Install, remove, and manage packages via npm or pip."
    parameters_schema = {
        "type": "object",
        "properties": {
            "manager": {"type": "string", "enum": ["npm", "pip"]},
            "action": {"type": "string", "enum": ["install", "remove", "update", "list"]},
            "packages": {"type": "string", "description": "Space-separated list of packages."}
        },
        "required": ["manager", "action"]
    }

    def __init__(self, workspace_root: str):
        super().__init__()
        self.workspace_root = workspace_root
        self.logger = logging.getLogger("PackageManager")

    def _run(self, manager: str, action: str, **kwargs) -> str:
        packages = kwargs.get("packages", "")
        if manager == "npm":
            return self._run_npm(action, packages)
        elif manager == "pip":
            return self._run_pip(action, packages)
        else:
            return f"Error: Manager {manager} not supported."

    def _run_npm(self, action: str, packages: str) -> str:
        cmd = ["npm"]
        if action == "install":
            cmd += ["install", packages] if packages else ["install"]
        elif action == "remove":
            cmd += ["uninstall", packages]
        elif action == "update":
            cmd += ["update", packages] if packages else ["update"]
        elif action == "list":
            cmd += ["list", "--depth=0"]

        try:
            result = subprocess.run(cmd, cwd=self.workspace_root, capture_output=True, text=True, check=True)
            return f"npm {action} completed successfully:\n{result.stdout}"
        except subprocess.CalledProcessError as e:
            return f"npm {action} failed: {e.stderr}"

    def _run_pip(self, action: str, packages: str) -> str:
        # Determine the pip executable (pip or pip3)
        pip_cmd = "pip3" if subprocess.run(["pip3", "--version"], capture_output=True).returncode == 0 else "pip"
        
        cmd = [pip_cmd]
        if action == "install":
            cmd += ["install", packages] if packages else ["install", "-r", "requirements.txt"]
        elif action == "remove":
            cmd += ["uninstall", "-y", packages]
        elif action == "update":
            cmd += ["install", "--upgrade", packages]
        elif action == "list":
            cmd += ["list"]

        try:
            result = subprocess.run(cmd, cwd=self.workspace_root, capture_output=True, text=True, check=True)
            return f"{pip_cmd} {action} completed successfully:\n{result.stdout}"
        except subprocess.CalledProcessError as e:
            return f"{pip_cmd} {action} failed: {e.stderr}"

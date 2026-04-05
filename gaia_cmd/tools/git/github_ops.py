import os
import subprocess
import logging
from typing import Any, Dict
from gaia_cmd.core.tools.base import BaseTool

class GitHubTool(BaseTool):
    """
    Advanced GitHub integration tool.
    Handles repository creation, branch management, and syncing with GitHub.
    Uses 'gh' CLI if available, otherwise falls back to basic 'git' with tokens.
    """
    name = "github_manager"
    description = "Manage GitHub repositories: create, push, and manage branches."
    parameters_schema = {
        "type": "object",
        "properties": {
            "action": {"type": "string", "enum": ["create_repo", "push", "create_branch", "create_pr"]},
            "repo_name": {"type": "string"},
            "branch_name": {"type": "string"},
            "visibility": {"type": "string", "default": "public"}
        },
        "required": ["action"]
    }

    def __init__(self, workspace_root: str, github_token: str = None, github_user: str = None):
        super().__init__()
        self.workspace_root = workspace_root
        self.github_token = github_token
        self.github_user = github_user
        self.logger = logging.getLogger("GitHubTool")

    def _run(self, action: str, **kwargs) -> str:
        if action == "create_repo":
            return self._create_repo(kwargs.get("repo_name"), kwargs.get("visibility", "public"))
        elif action == "push":
            return self._push(kwargs.get("branch_name", "main"))
        elif action == "create_branch":
            return self._create_branch(kwargs.get("branch_name"))
        else:
            return f"Action {action} not yet implemented."

    def _create_repo(self, repo_name: str, visibility: str) -> str:
        if not repo_name:
            repo_name = os.path.basename(self.workspace_root)
            
        try:
            # Check if gh CLI is installed
            subprocess.run(["gh", "--version"], capture_output=True, check=True)
            cmd = ["gh", "repo", "create", repo_name, f"--{visibility}", "--source=.", "--push"]
            result = subprocess.run(cmd, cwd=self.workspace_root, capture_output=True, text=True, check=True)
            return f"Successfully created GitHub repository '{repo_name}' and pushed code."
        except:
            return f"Failed to create repo via gh CLI. Please ensure 'gh' is installed and authenticated."

    def _push(self, branch: str) -> str:
        try:
            subprocess.run(["git", "push", "origin", branch], cwd=self.workspace_root, capture_output=True, check=True)
            return f"Pushed current changes to GitHub branch '{branch}'."
        except subprocess.CalledProcessError as e:
            return f"Failed to push: {e.stderr}"

    def _create_branch(self, branch_name: str) -> str:
        if not branch_name:
            return "Error: branch_name is required."
        try:
            subprocess.run(["git", "checkout", "-b", branch_name], cwd=self.workspace_root, capture_output=True, check=True)
            return f"Created and switched to new branch '{branch_name}'."
        except subprocess.CalledProcessError as e:
            return f"Failed to create branch: {e.stderr}"

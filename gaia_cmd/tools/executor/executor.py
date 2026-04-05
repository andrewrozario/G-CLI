import logging
from typing import Any, Dict
from gaia_cmd.core.tools.registry import ToolRegistry
from gaia_cmd.tools.fs.file_ops import ReadFileTool, WriteFileTool, EditFileTool, CopyDirectoryTool, RenameFileTool
from gaia_cmd.tools.shell.runner import ShellCommandTool
from gaia_cmd.tools.git.ops import GitTool
from gaia_cmd.tools.git.github_ops import GitHubTool
from gaia_cmd.tools.shell.package_manager import PackageManagerTool
from gaia_cmd.tools.web.search import WebSearchTool

class ToolExecutor:
    """
    The main interface for agents to execute tools.
    It initializes the registry, loads all safe tools, and routes execution requests.
    """
    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root
        self.logger = logging.getLogger("ToolExecutor")
        
        self.registry = ToolRegistry()
        self._register_default_tools()

    def _register_default_tools(self):
        """
        Instantiates and registers all available tools into the system.
        """
        tools = [
            ReadFileTool(self.workspace_root),
            WriteFileTool(self.workspace_root),
            EditFileTool(self.workspace_root),
            CopyDirectoryTool(self.workspace_root),
            RenameFileTool(self.workspace_root),
            ShellCommandTool(self.workspace_root),
            GitTool(self.workspace_root),
            GitHubTool(self.workspace_root),
            PackageManagerTool(self.workspace_root),
            WebSearchTool()
        ]
        
        for tool in tools:
            self.registry.register(tool)

    def get_available_tools_schema(self):
        """
        Used by the Orchestrator to inject tool capabilities into the LLM prompt.
        """
        return self.registry.get_all_schemas()

    def execute_tool(self, name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Routes the tool call through the safe registry execution.
        """
        self.logger.info(f"Agent requested execution of tool: '{name}'")
        return self.registry.execute_tool(name, params)

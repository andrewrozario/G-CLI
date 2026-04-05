import logging
from typing import Dict, List, Any
from gaia_cmd.core.tools.base import BaseTool

class ToolRegistry:
    """
    Manages all available tools in the system.
    Agents query this registry to find out what they can do and execute tools securely.
    """
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self.logger = logging.getLogger("ToolRegistry")

    def register(self, tool: BaseTool) -> None:
        """
        Registers a new tool into the system.
        """
        if tool.name in self.tools:
            self.logger.warning(f"Tool '{tool.name}' is already registered. Overwriting.")
        self.tools[tool.name] = tool
        self.logger.info(f"Registered tool: '{tool.name}'")

    def get_tool(self, name: str) -> BaseTool:
        """
        Retrieves a tool by name.
        """
        return self.tools.get(name)

    def get_all_schemas(self) -> List[Dict[str, Any]]:
        """
        Returns the JSON Schema definitions for all registered tools.
        This is injected into the LLM prompt so it knows how to call them.
        """
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters_schema
            }
            for tool in self.tools.values()
        ]

    def execute_tool(self, name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a tool by name with the given parameters.
        """
        tool = self.get_tool(name)
        if not tool:
            self.logger.error(f"Attempted to execute unknown tool: {name}")
            return {"status": "error", "message": f"Tool '{name}' not found in registry."}
        return tool.execute(**params)

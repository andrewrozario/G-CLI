import abc
import logging
from typing import Any, Dict

class BaseTool(abc.ABC):
    """
    Abstract Base Class for all tools.
    Provides built-in logging, error handling, and a standard interface.
    """
    name: str = ""
    description: str = ""
    parameters_schema: Dict[str, Any] = {}

    def __init__(self):
        self.logger = logging.getLogger(f"Tool.{self.name}")

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        The safe execution wrapper. Logs the attempt and catches errors.
        """
        self.logger.info(f"Executing tool '{self.name}' with params: {kwargs}")
        try:
            result = self._run(**kwargs)
            self.logger.debug(f"Tool '{self.name}' execution successful. Result: {result}")
            return {"status": "success", "data": result}
        except PermissionError as pe:
            self.logger.warning(f"Tool '{self.name}' execution blocked by permission: {str(pe)}")
            return {"status": "error", "message": f"Permission Denied: {str(pe)}"}
        except Exception as e:
            self.logger.error(f"Tool '{self.name}' execution failed: {str(e)}")
            return {"status": "error", "message": str(e)}

    @abc.abstractmethod
    def _run(self, **kwargs) -> Any:
        """
        The actual implementation of the tool's logic. Must be overridden.
        """
        pass

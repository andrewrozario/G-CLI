import logging
import threading
from typing import Any, Dict, List

class ShortTermMemory:
    """
    Manages the current session's state, active context, and recent actions.
    Thread-safe implementation for parallel agent execution.
    """
    def __init__(self):
        self.logger = logging.getLogger("ShortTermMemory")
        self.current_task: str = ""
        self.active_files: set = set()
        self.recent_actions: List[Dict[str, Any]] = []
        self.max_actions = 10 
        self._lock = threading.Lock()

    def set_task(self, task: str):
        with self._lock:
            self.current_task = task
            self.logger.debug(f"Current task set to: {task}")

    def add_active_file(self, file_path: str):
        with self._lock:
            self.active_files.add(file_path)

    def remove_active_file(self, file_path: str):
        with self._lock:
            if file_path in self.active_files:
                self.active_files.remove(file_path)

    def add_action(self, action: str, result: str):
        with self._lock:
            self.recent_actions.append({"action": action, "result": result})
            if len(self.recent_actions) > self.max_actions:
                self.recent_actions.pop(0)

    def get_context(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "current_task": self.current_task,
                "active_files": list(self.active_files),
                "recent_actions": list(self.recent_actions)
            }

    def clear(self):
        with self._lock:
            self.current_task = ""
            self.active_files.clear()
            self.recent_actions.clear()

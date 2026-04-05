from typing import Any, Dict, List, Optional
from gaia_cmd.agents.base import BaseAgent
from gaia_cmd.core.communication.message import Message
from gaia_cmd.core.memory.manager import MemoryManager

class MemoryAgent(BaseAgent):
    """
    Advanced Memory Agent responsible for global knowledge persistence,
    pattern recognition, and cross-project learning.
    Think of it as the 'Brain' that ensures Gaia CLI gets smarter over time.
    """
    def __init__(self, memory_manager: MemoryManager):
        super().__init__("memory", "Stores and retrieves persistent cross-project knowledge")
        self.memory = memory_manager

    def process_message(self, message: Message) -> Message:
        content = message.content
        if not isinstance(content, dict):
            return self.send_message(message.sender, {"success": False, "error": "Content must be dict"}, message.task_id)

        action = content.get("action")
        try:
            if action == "get_context":
                # Get full context including global patterns
                task = content.get("task", "")
                context = self.memory.build_prompt_context(task)
                return self.send_message(message.sender, {"success": True, "context": context}, message.task_id)
            
            elif action == "record_action":
                self.memory.record_action(content.get("action_desc", ""), content.get("result", ""))
                return self.send_message(message.sender, {"success": True}, message.task_id)
            
            elif action == "learn":
                # Deep Learning: Store a pattern/mistake globally
                self.memory.learn_from_feedback(
                    task=content.get("task_description", ""),
                    success=content.get("success", True),
                    diagnosis=content.get("diagnosis", ""),
                    tags=content.get("tags", [])
                )
                return self.send_message(message.sender, {"success": True}, message.task_id)
            
            elif action == "store_architecture":
                # Explicitly store an architectural rule
                self.memory.add_insight(
                    category="architecture",
                    insight=content.get("fact", ""),
                    tags=["architecture"] + content.get("tags", [])
                )
                return self.send_message(message.sender, {"success": True}, message.task_id)
            
            elif action == "search_patterns":
                # Explicitly search for past patterns
                query = content.get("query", "")
                results = self.memory.global_memory.search(query, category="pattern")
                return self.send_message(message.sender, {"success": True, "results": results}, message.task_id)
                
            else:
                return self.send_message(message.sender, {"success": False, "error": f"Unknown action: {action}"}, message.task_id)
        except Exception as e:
            self.logger.error(f"Memory Agent error: {e}")
            return self.send_message(message.sender, {"success": False, "error": str(e)}, message.task_id)

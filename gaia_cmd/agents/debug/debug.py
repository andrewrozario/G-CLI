from typing import Any, Dict
from gaia_cmd.agents.base import BaseAgent
from gaia_cmd.core.communication.message import Message
from gaia_cmd.core.llm.provider import LLMProvider
from gaia_cmd.core.debugging.engine import DebugEngine
from gaia_cmd.core.prompt.role_config import RoleConfig, AgentRole

class DebugAgent(BaseAgent):
    """
    Debug Agent responsible for detecting errors, running tests, and fixing issues.
    """
    def __init__(self, llm: LLMProvider, debug_engine: DebugEngine):
        super().__init__("debug", "Detects and fixes errors, runs tests")
        self.llm = llm
        self.debug_engine = debug_engine

    def process_message(self, message: Message) -> Message:
        content = message.content
        if not isinstance(content, dict):
            return self.send_message(message.sender, {"success": False, "error": "Content must be dict"}, message.task_id)

        action = content.get("action")
        if action == "diagnose_and_fix":
            error_msg = content.get("error_msg", "")
            step_desc = content.get("step_description", "")
            
            # Inject role-based thinking into DebugEngine if it supports it, 
            # or wrap the output with role instructions for internal LLM calls.
            # For now, we wrap the analyze call if possible or just prepend.
            
            system_instruction = RoleConfig.get_role_prompt(AgentRole.DEBUGGER)
            diagnosis = self.debug_engine.analyze_and_suggest_fix(f"{system_instruction}\n\nERROR: {error_msg}", step_desc)
            
            return self.send_message(message.sender, {"success": True, "diagnosis": diagnosis}, message.task_id)
        elif action == "record_fix":
            self.debug_engine.record_successful_fix(content.get("error_msg", ""), "Fixed by automatic retry / dynamic patch", content.get("step_description", ""))
            return self.send_message(message.sender, {"success": True}, message.task_id)
        else:
            return self.send_message(message.sender, {"success": False, "error": f"Unknown action: {action}"}, message.task_id)

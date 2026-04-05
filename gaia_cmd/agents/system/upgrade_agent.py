import logging
import json
import os
from typing import Any, Dict, List, Optional
from gaia_cmd.agents.base import BaseAgent
from gaia_cmd.core.communication.message import Message
from gaia_cmd.core.llm.provider import LLMProvider
from gaia_cmd.core.llm.safe_generate import safe_generate
from gaia_cmd.core.system.upgrade_manager import UpgradeManager

class UpgradeAgent(BaseAgent):
    """
    Gaia CLI Self-Upgrade Agent.
    Analyzes Gaia's own code and suggests/applies improvements.
    """
    def __init__(self, llm: LLMProvider, workspace_root: str):
        super().__init__("system_upgrader", "Analyzes and upgrades Gaia CLI's own modules")
        self.llm = llm
        self.upgrade_manager = UpgradeManager(workspace_root)

    def process_message(self, message: Message) -> Message:
        content = message.content
        if not isinstance(content, dict):
            return self.send_message(message.sender, {"success": False, "error": "Content must be dict"}, message.task_id)

        action = content.get("action")
        try:
            if action == "analyze_self":
                # Analyze a specific module for improvements
                module = content.get("module_path")
                analysis = self._analyze_module(module)
                return self.send_message(message.sender, {"success": True, "analysis": analysis}, message.task_id)
            
            elif action == "apply_upgrade":
                # Apply suggested improvements
                module = content.get("module_path")
                new_code = content.get("new_code")
                success = self._execute_upgrade(module, new_code)
                return self.send_message(message.sender, {"success": success}, message.task_id)
                
            else:
                return self.send_message(message.sender, {"success": False, "error": f"Unknown action: {action}"}, message.task_id)
        except Exception as e:
            self.logger.error(f"Upgrade Agent error: {e}")
            return self.send_message(message.sender, {"success": False, "error": str(e)}, message.task_id)

    def _analyze_module(self, module_path: str) -> Dict[str, Any]:
        """Uses LLM to find potential improvements in Gaia's own code."""
        full_path = os.path.join(self.upgrade_manager.workspace_root, module_path)
        with open(full_path, 'r') as f:
            code = f.read()

        system_prompt = (
            "You are the Gaia CLI Meta-Architect. Your goal is to improve Gaia's own codebase. "
            "Analyze the provided module for: efficiency, bug potential, and feature gaps.\n"
            "Respond with JSON: {'improvements': '...', 'suggested_code': '...', 'priority': 'low/med/high'}"
        )
        
        response = safe_generate(self.llm, [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"MODULE: {module_path}\nCODE:\n{code}"}
        ], task_description=f"Self-audit: {module_path}")
        
        # Parse JSON from response...
        # (Simplified for now)
        return {"raw_response": response}

    def _execute_upgrade(self, module_path: str, new_code: str) -> bool:
        """Backs up and applies the upgrade."""
        backup = self.upgrade_manager.prepare_upgrade(module_path)
        if not backup and os.path.exists(os.path.join(self.upgrade_manager.workspace_root, module_path)):
            return False
            
        success = self.upgrade_manager.apply_patch(module_path, new_code)
        if success:
            self.upgrade_manager.finalize_upgrade()
            return True
        else:
            if backup:
                self.upgrade_manager.rollback(module_path, backup)
            return False

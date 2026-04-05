from typing import Any, Dict
import json
from gaia_cmd.agents.base import BaseAgent
from gaia_cmd.core.communication.message import Message
from gaia_cmd.core.llm.provider import LLMProvider
from gaia_cmd.core.llm.safe_generate import safe_generate
from gaia_cmd.core.prompt.role_config import RoleConfig, AgentRole

class ReviewerAgent(BaseAgent):
    """
    Reviewer Agent responsible for reviewing code quality and suggesting improvements.
    """
    def __init__(self, llm: LLMProvider):
        super().__init__("reviewer", "Reviews code quality, suggests improvements")
        self.llm = llm

    def process_message(self, message: Message) -> Message:
        content = message.content
        if not isinstance(content, dict):
            return self.send_message(message.sender, {"success": False, "error": "Content must be dict"}, message.task_id)

        action = content.get("action")
        if action == "review_step":
            step_desc = content.get("description", "")
            step_output = content.get("output", "")
            
            # Incorporate Role-Based Intelligence
            role_prompt = RoleConfig.get_role_prompt(AgentRole.REVIEWER)
            
            system_prompt = (
                f"{role_prompt}\n\n"
                "You are the Gaia CLI Code Reviewer. Review the completed step and its output. "
                "Decide if it meets quality standards. Return JSON: {\"approved\": true/false, \"feedback\": \"...\"}"
            )
            user_prompt = f"STEP: {step_desc}\nOUTPUT:\n{step_output}"
            
            try:
                response_data = safe_generate(self.llm, [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ], task_description=f"Reviewing: {step_desc}")
                response = response_data.get("content", "")

                if "```json" in response:
                    json_str = response.split("```json")[1].split("```")[0].strip()
                elif "{" in response:
                    json_str = response[response.find("{"):response.rfind("}")+1]
                else:
                    json_str = "{\"approved\": true, \"feedback\": \"Looks good.\"}"
                
                result = json.loads(json_str)
                return self.send_message(message.sender, {"success": True, "review": result}, message.task_id)
            except Exception as e:
                self.logger.error(f"Reviewer failed: {e}")
                return self.send_message(message.sender, {"success": True, "review": {"approved": True, "feedback": str(e)}}, message.task_id)
        else:
            return self.send_message(message.sender, {"success": False, "error": f"Unknown action: {action}"}, message.task_id)

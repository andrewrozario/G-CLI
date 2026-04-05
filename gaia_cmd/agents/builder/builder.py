from typing import Any, Dict, List
import json
from gaia_cmd.agents.base import BaseAgent
from gaia_cmd.core.communication.message import Message
from gaia_cmd.core.llm.provider import LLMProvider
from gaia_cmd.core.llm.safe_generate import safe_generate
from gaia_cmd.tools.executor.executor import ToolExecutor
from gaia_cmd.core.prompt.manager import PromptOrchestrator, PromptMode
from gaia_cmd.core.prompt.role_config import AgentRole
from gaia_cmd.core.learning.reflection import ReflectionEngine

class BuilderAgent(BaseAgent):
    """
    Builder Agent responsible for writing code, creating files, and implementing features.
    Now with a Reflection System to analyze and improve its own performance.
    """
    def __init__(self, llm: LLMProvider, executor: ToolExecutor, prompt_engine: PromptOrchestrator, 
                 name: str = "builder", role: AgentRole = AgentRole.BUILDER):
        super().__init__(name, "Writes code, creates files, implements features")
        self.llm = llm
        self.executor = executor
        self.prompt_engine = prompt_engine
        self.role = role
        # Initialize Reflection Engine with shared memory and LLM
        self.reflection_engine = ReflectionEngine(self.llm, self.prompt_engine.memory)

    def process_message(self, message: Message) -> Message:
        content = message.content
        if not isinstance(content, dict):
            return self.send_message(message.sender, {"success": False, "error": "Content must be dict"}, message.task_id)

        action = content.get("action")
        if action == "execute_step":
            result = self.execute_step(content)
            return self.send_message(message.sender, result, message.task_id)
        else:
            return self.send_message(message.sender, {"success": False, "error": f"Unknown action: {action}"}, message.task_id)

    def execute_step(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        step_desc = payload.get("description", "")
        step_goal = payload.get("goal", "")
        req_files = payload.get("required_files", [])
        
        max_turns = 5
        turn = 0
        step_history = []
        
        while turn < max_turns:
            turn += 1
            
            # Use PromptOrchestrator to get the full payload including role intelligence
            messages = self.prompt_engine.get_task_payload(
                task=f"STEP: {step_desc}\nGOAL: {step_goal}\nREQUIRED FILES: {req_files}",
                mode=PromptMode.CODING,
                agent_role=self.role
            )
            
            for h in step_history:
                messages.append(h)

            try:
                response_data = safe_generate(self.llm, messages, task_description=step_desc)
                response = response_data.get("content", "")
                
                if "TASK COMPLETE" in response.upper() or "STEP COMPLETE" in response.upper():
                    result = {"success": True, "output": response}
                    # Trigger Self-Reflection after completion
                    self.reflection_engine.reflect_on_task(step_desc, result, step_history)
                    return result

                try:
                    if "```json" in response:
                        json_str = response.split("```json")[1].split("```")[0].strip()
                    elif "{" in response:
                        json_str = response[response.find("{"):response.rfind("}")+1]
                    else:
                        json_str = "{}"
                        
                    tool_call = json.loads(json_str)
                    tool_name = tool_call.get("tool")
                    tool_params = tool_call.get("params", {})
                    
                    if tool_name:
                        self.logger.info(f"{self.name} using tool: {tool_name}")
                        result = self.executor.execute_tool(tool_name, tool_params)
                        step_history.append({"role": "assistant", "content": response})
                        step_history.append({"role": "user", "content": f"TOOL RESULT ({tool_name}): {result}"})
                    else:
                        step_history.append({"role": "assistant", "content": response})
                        step_history.append({"role": "user", "content": "Please continue until the step is complete. If you are done, say 'STEP COMPLETE'."})
                        
                except json.JSONDecodeError:
                    step_history.append({"role": "assistant", "content": response})
                    step_history.append({"role": "user", "content": "Invalid tool call format. Please use: {\"tool\": \"name\", \"params\": {...}}"})

            except Exception as e:
                self.logger.error(f"Error in {self.name} turn {turn}: {e}")
                result = {"success": False, "error": str(e)}
                # Trigger Self-Reflection on error
                self.reflection_engine.reflect_on_task(step_desc, result, step_history)
                return result

        result = {"success": False, "error": f"Max turns ({max_turns}) reached for step."}
        # Trigger Self-Reflection on timeout
        self.reflection_engine.reflect_on_task(step_desc, result, step_history)
        return result

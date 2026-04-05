import logging
import json
from typing import Any, Dict, Optional
from gaia_cmd.core.llm.provider import LLMProvider
from gaia_cmd.core.llm.safe_generate import safe_generate
from gaia_cmd.core.planning.models import ExecutionPlan, TaskStep, SystemDesign
from gaia_cmd.agents.base import BaseAgent
from gaia_cmd.core.communication.message import Message
from gaia_cmd.core.prompt.role_config import RoleConfig, AgentRole

class PlannerAgent(BaseAgent):
    """
    Strategic Planner Agent.
    Operates in 'Strategic Mode' to design systems, architectures, and identify risks
    before generating a task-based execution plan.
    """
    def __init__(self, llm: LLMProvider):
        super().__init__("planner", "Designs system architecture, tech stacks, and breaks tasks into strategic steps")
        self.llm = llm

    def process_message(self, message: Message) -> Message:
        content = message.content
        if not isinstance(content, dict):
            return self.send_message(message.sender, {"error": "Content must be a dict"}, message.task_id)

        action = content.get("action")
        try:
            if action == "create_plan":
                plan = self.create_initial_plan(content.get("goal"), content.get("context", {}))
                return self.send_message(message.sender, {"plan": plan}, message.task_id)
            elif action == "replan":
                plan = self.replan(
                    content.get("current_plan"),
                    content.get("current_state", {}),
                    content.get("failure_report")
                )
                return self.send_message(message.sender, {"plan": plan}, message.task_id)
            else:
                return self.send_message(message.sender, {"error": f"Unknown action: {action}"}, message.task_id)
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            return self.send_message(message.sender, {"error": str(e)}, message.task_id)

    def create_initial_plan(self, goal: str, context: Dict[str, Any]) -> ExecutionPlan:
        """
        Generates a strategic execution plan including a System Design phase.
        """
        self.logger.info(f"Generating strategic plan for: {goal}")
        
        prompt_payload = context.get("prompt")
        
        try:
            if prompt_payload:
                response_data = safe_generate(self.llm, prompt_payload, task_description=goal)
                response = response_data.get("content", "")
            else:
                system_prompt = (
                    f"{RoleConfig.get_role_prompt(AgentRole.PLANNER)}\n\n"
                    "You are the Gaia CLI Strategic Architect. Your job is to design a robust, scalable system "
                    "before implementation. You must provide a high-level System Design followed by a sequence of "
                    "atomic, verifiable steps.\n\n"
                    "STRATEGIC GUIDELINES:\n"
                    "1. Architecture: Choose between Modular, Microservices, Event-Driven, or Layered based on the goal.\n"
                    "2. Tech Stack: Select appropriate languages/frameworks based on the existing environment.\n"
                    "3. Risks: Identify potential bottlenecks, security concerns, or technical debt.\n"
                    "4. Dependencies: Ensure steps are ordered by their logical implementation requirements.\n\n"
                    "Respond ONLY with a valid JSON object."
                )
                
                user_prompt = (
                    f"GOAL: {goal}\n"
                    f"CONTEXT: {context}\n\n"
                    "Return a JSON execution plan with the following structure:\n"
                    "{\n"
                    "  \"design\": {\n"
                    "    \"architecture_type\": \"modular/layered/etc\",\n"
                    "    \"tech_stack\": {\"backend\": \"Python/Node\", \"db\": \"SQLite/Postgres\"},\n"
                    "    \"components\": [{\"name\": \"Component A\", \"purpose\": \"...\"}],\n"
                    "    \"risks\": [{\"risk\": \"...\", \"mitigation\": \"...\"}],\n"
                    "    \"reasoning\": \"Explain why this design was chosen\"\n"
                    "  },\n"
                    "  \"steps\": [\n"
                    "    {\n"
                    "      \"id\": \"step_id\",\n"
                    "      \"description\": \"Detailed description\",\n"
                    "      \"goal\": \"Verification criteria\",\n"
                    "      \"dependencies\": [],\n"
                    "      \"required_files\": [],\n"
                    "      \"required_tools\": []\n"
                    "    }\n"
                    "  ]\n"
                    "}\n"
                )
                
                response_data = safe_generate(self.llm, [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ], task_description=goal)
                response = response_data.get("content", "")
            
            # Clean response text
            if "```json" in response:
                response_text = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response_text = response.split("```")[1].split("```")[0].strip()
            else:
                response_text = response
            
            plan_data = json.loads(response_text)
            design = SystemDesign.from_dict(plan_data.get("design"))
            
            plan = ExecutionPlan(goal, design=design)
            for step_data in plan_data.get("steps", []):
                step = TaskStep(
                    id=step_data["id"],
                    description=step_data["description"],
                    goal=step_data.get("goal", ""),
                    dependencies=step_data.get("dependencies", []),
                    required_files=step_data.get("required_files", []),
                    required_tools=step_data.get("required_tools", [])
                )
                plan.add_step(step)
            return plan
            
        except Exception as e:
            self.logger.error(f"Strategic Planning failed: {e}. Falling back to basic plan.")
            plan = ExecutionPlan(goal)
            plan.add_step(TaskStep(id="fallback", description=f"Execute task: {goal}", goal="Task completed"))
            return plan

    def replan(self, current_plan: ExecutionPlan, current_state: Dict[str, Any], failure_report: Optional[str] = None) -> ExecutionPlan:
        """
        Adjusts the strategic plan based on execution failures.
        """
        self.logger.info(f"Replanning based on failure: {failure_report}")
        if not current_plan:
            return current_plan
            
        system_prompt = (
            f"{RoleConfig.get_role_prompt(AgentRole.PLANNER)}\n\n"
            "You are the Gaia CLI Strategic Architect. A step in the current execution plan failed. "
            "Analyze the failure and provide a REVISED JSON execution plan. "
            "Maintain the original architecture and design unless the failure indicates a structural flaw."
        )
        
        user_prompt = (
            f"ORIGINAL GOAL: {current_plan.goal}\n"
            f"CURRENT DESIGN: {current_plan.design.to_dict() if current_plan.design else 'None'}\n"
            f"CURRENT PLAN STATE: {current_plan.to_dict()}\n"
            f"FAILURE REPORT: {failure_report}\n"
            f"CURRENT WORKSPACE STATE: {current_state}\n\n"
            "Return the FULL revised JSON execution plan (design and steps)."
        )
        
        try:
            response_data = safe_generate(self.llm, [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ], task_description=f"Replanning: {current_plan.goal}")
            response = response_data.get("content", "")

            if "```json" in response:
                response_text = response.split("```json")[1].split("```")[0].strip()
            else:
                response_text = response
            
            plan_data = json.loads(response_text)
            design = SystemDesign.from_dict(plan_data.get("design"))
            
            new_plan = ExecutionPlan(current_plan.goal, design=design)
            for step_data in plan_data.get("steps", []):
                step = TaskStep(
                    id=step_data["id"],
                    description=step_data["description"],
                    goal=step_data.get("goal", ""),
                    dependencies=step_data.get("dependencies", []),
                    required_files=step_data.get("required_files", []),
                    required_tools=step_data.get("required_tools", [])
                )
                old_step = next((s for s in current_plan.steps.values() if s.id == step.id), None)
                if old_step and step.description == old_step.description:
                    step.status = old_step.status
                
                new_plan.add_step(step)
            return new_plan
            
        except Exception as e:
            self.logger.error(f"LLM Replanning failed: {e}. Returning original plan.")
            return current_plan

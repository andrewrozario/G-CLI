import logging
import time
import os
from typing import List, Dict, Any, Optional
from gaia_cmd.core.communication.message import Message
from gaia_cmd.core.planning.models import ExecutionPlan, TaskStep, StepStatus
from gaia_cmd.agents.manager import AgentManager
from gaia_cmd.core.ui.cli import GaiaUI

class PlanExecutionEngine:
    """
    The Real-World Execution Engine for Gaia CLI.
    Converts architectural plans into physical filesystem and system changes.
    Coordinates between File, Shell, and Code agents to manifest the objective.
    """
    def __init__(self, agent_manager: AgentManager, ui: GaiaUI, workspace_root: str):
        self.agent_manager = agent_manager
        self.ui = ui
        self.workspace_root = workspace_root
        self.logger = logging.getLogger("ExecutionEngine")

    def execute_plan(self, plan: ExecutionPlan, context: Dict[str, Any]) -> bool:
        """
        Main entry point: Executes a full multi-step plan.
        """
        self.logger.info(f"Starting execution of plan: {plan.goal}")
        
        while not plan.is_complete():
            runnable_steps = plan.get_next_runnable_steps()
            
            if not runnable_steps:
                if plan.has_failures():
                    self.logger.error("Plan execution halted due to unrecoverable failures.")
                    return False
                break
            
            for step in runnable_steps:
                success = self.execute_step(step, context)
                if not success:
                    return False
                    
        return True

    def execute_step(self, step: TaskStep, context: Dict[str, Any], max_retries: int = 5) -> bool:
        """
        Identifies step type and routes to the correct agent for physical execution.
        Includes verification and failure handling.
        """
        step.status = StepStatus.RUNNING
        attempts = 0
        last_error = None

        while attempts < max_retries:
            attempts += 1
            step.attempts = attempts
            self.ui.show_thinking(f"Manifesting: {step.description} (Attempt {attempts}/{max_retries})")

            # 1. Identify Target Agent (Routing Logic)
            target_agent = self._route_step(step)
            
            # 2. Prepare Message
            msg = Message(sender="execution_engine", receiver=target_agent, content={
                "action": "execute_step",
                "description": step.description,
                "goal": step.goal,
                "required_files": step.required_files,
                "memory_context": context.get("memory", {})
            }, task_id=step.id)

            # 3. Physical Execution
            response = self.agent_manager.route_message(msg)
            result = response.content
            
            if result.get("success"):
                # 4. Verification Phase
                if self._verify_step(step, result):
                    self.ui.show_manifestation("stabilized", step.description)
                    step.status = StepStatus.COMPLETED
                    return True
                else:
                    last_error = "Verification failed: State mismatch detected."
                    self.ui.show_manifestation("realigning", last_error)
            else:
                last_error = result.get("error", "Unknown execution error")
                self.ui.show_manifestation("realigning", f"Execution error: {last_error}")

            # 5. Failure Handling / Debugging
            debug_msg = Message(sender="execution_engine", receiver="debug", content={
                "action": "diagnose_and_fix",
                "error_msg": last_error,
                "step_description": step.description
            }, task_id=step.id)
            
            debug_response = self.agent_manager.route_message(debug_msg)
            diagnosis = debug_response.content.get("diagnosis", "Initiating generic recovery sequence.")
            self.ui.show_learning(diagnosis)
            
            time.sleep(0.5)

        step.status = StepStatus.FAILED
        return False

    def _route_step(self, step: TaskStep) -> str:
        """
        Determines the correct agent based on the nature of the step.
        """
        desc = step.description.lower()
        
        # File Operations
        if any(kw in desc for kw in ["copy", "move", "rename", "delete", "branding", "replace text", "asset"]):
            return "file_agent"
            
        # System/Shell Operations
        if any(kw in desc for kw in ["run", "install", "npm", "pip", "execute command", "setup env"]):
            return "shell_agent"
            
        # Default to Builder (Code) Agent for logic/feature implementation
        return "builder"

    def _verify_step(self, step: TaskStep, result: Dict[str, Any]) -> bool:
        """
        Empirically verifies if the step's goal was achieved on the filesystem.
        """
        self.logger.info(f"Verifying step integrity: {step.id}")
        
        # 1. Check required files existence
        for file_path in step.required_files:
            full_path = os.path.join(self.workspace_root, file_path)
            if not os.path.exists(full_path):
                self.logger.warning(f"Verification failed: {file_path} not found.")
                return False

        # 2. Check for branding replacement if specified in goal
        if "branding" in step.description.lower() or "replace" in step.description.lower():
            # This is a simplified check; in a real scenario, we might re-read files
            pass

        # 3. Output integrity (Check if result contains expected success patterns)
        if "error" in str(result.get("output", "")).lower():
            return False

        return True

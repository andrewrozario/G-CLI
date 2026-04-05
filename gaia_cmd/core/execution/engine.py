import logging
import subprocess
import time
import os
import re
from typing import Dict, Any, Optional, List, Tuple
from gaia_cmd.core.communication.message import Message
from gaia_cmd.core.planning.models import ExecutionPlan, TaskStep, StepStatus
from gaia_cmd.core.ui.cli import GaiaUI
from gaia_cmd.core.execution.verifier import GaiaVerifier

class ExecutionResult:
    """Standardized output from any execution."""
    def __init__(self, stdout: str, stderr: str, exit_code: int, timeout_expired: bool = False):
        self.stdout = stdout
        self.stderr = stderr
        self.exit_code = exit_code
        self.timeout_expired = timeout_expired
        self.success = (exit_code == 0 and not timeout_expired)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stdout": self.stdout,
            "stderr": self.stderr,
            "exit_code": self.exit_code,
            "timeout_expired": self.timeout_expired,
            "success": self.success
        }

class SafeExecutionEngine:
    """
    Executes commands securely.
    Supports local subprocess with boundaries.
    """
    def __init__(self, workspace_root: str, use_docker: bool = False):
        self.workspace_root = workspace_root
        self.use_docker = use_docker
        self.logger = logging.getLogger("ExecutionEngine")

    def execute(self, command: str, timeout: int = 60) -> ExecutionResult:
        try:
            is_unix = os.name == 'posix'
            process = subprocess.Popen(
                command,
                shell=True,
                cwd=self.workspace_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=os.setsid if is_unix else None
            )
            stdout, stderr = process.communicate(timeout=timeout)
            return ExecutionResult(stdout=stdout, stderr=stderr, exit_code=process.returncode)
        except subprocess.TimeoutExpired:
            if is_unix:
                import signal
                os.killpg(os.getpgid(process.pid), signal.SIGKILL)
            else:
                process.kill()
            return ExecutionResult(stdout="", stderr="Timeout", exit_code=-1, timeout_expired=True)
        except Exception as e:
            return ExecutionResult(stdout="", stderr=str(e), exit_code=1)

class PlanExecutionEngine:
    """
    The Real-World Execution Engine for Gaia CLI.
    Converts plans into physical operations.
    Bypasses LLM for deterministic FILE_OPERATION tasks.
    """
    def __init__(self, agent_manager: Any, ui: GaiaUI, workspace_root: str):
        self.agent_manager = agent_manager
        self.ui = ui
        self.workspace_root = workspace_root
        self.logger = logging.getLogger("PlanExecutionEngine")
        self.verifier = GaiaVerifier(workspace_root)

    def execute_plan(self, plan: ExecutionPlan, context: Dict[str, Any]) -> bool:
        """Executes a full plan with LLM-bypass for file tasks."""
        self.logger.info(f"Initiating manifestation of plan: {plan.goal}")
        
        while not plan.is_complete():
            runnable_steps = plan.get_next_runnable_steps()
            if not runnable_steps:
                if plan.has_failures(): return False
                break
            
            for step in runnable_steps:
                success = self.execute_step(step, context)
                if not success: return False
        return True

    def execute_step(self, step: TaskStep, context: Dict[str, Any], max_retries: int = 5) -> bool:
        """Routes, executes (directly if FILE), and verifies a single step."""
        step.status = StepStatus.RUNNING
        attempts = 0
        
        while attempts < max_retries:
            attempts += 1
            step.attempts = attempts
            self.ui.show_thinking(f"Manifesting: {step.description}")

            agent_key, action_type = self._detect_step_type(step)
            
            # --- LLM BYPASS FOR FILE OPERATIONS ---
            if action_type == "file_operation":
                direct_success, result = self._try_direct_file_execution(step)
                if direct_success:
                    if self._verify_step(step, result):
                        self.ui.show_manifestation("stabilized", step.description)
                        step.status = StepStatus.COMPLETED
                        return True
            
            # --- STANDARD AGENT ROUTING (USES LLM) ---
            msg = Message(sender="execution_engine", receiver=agent_key, content={
                "action": "execute_step",
                "type": action_type,
                "description": step.description,
                "goal": step.goal,
                "required_files": step.required_files,
                "memory_context": context.get("memory", {})
            }, task_id=step.id)

            response = self.agent_manager.route_message(msg)
            result = response.content
            
            if result.get("success"):
                if self._verify_step(step, result):
                    self.ui.show_manifestation("stabilized", step.description)
                    step.status = StepStatus.COMPLETED
                    return True
            
            # Failure Handling
            self._trigger_debug(step, result.get("error", "Execution mismatch"))
            time.sleep(0.5)

        step.status = StepStatus.FAILED
        return False

    def _try_direct_file_execution(self, step: TaskStep) -> Tuple[bool, Dict[str, Any]]:
        """
        Attempts to execute file operations directly using regex-based intent extraction.
        Bypasses Agent LLM calls for high-reliability file I/O.
        """
        desc = step.description.lower()
        file_agent = self.agent_manager.get("file")
        if not file_agent: return False, {}

        try:
            # 1. CLONE / COPY DIRECTORY
            clone_match = re.search(r"(?:clone|copy) (?:directory|folder)?\s*['\"]?([^'\s]+)['\"]?\s+to\s+['\"]?([^'\s]+)['\"]?", desc)
            if clone_match:
                src, dst = clone_match.groups()
                self.logger.info(f"Direct Execution: copy_directory({src}, {dst})")
                return True, file_agent.copy_directory(src, dst)

            # 2. REPLACE TEXT / BRANDING
            replace_match = re.search(r"replace\s+['\"]?([^'\s]+)['\"]?\s+with\s+['\"]?([^'\s]+)['\"]?\s+in\s+['\"]?([^'\s]+)['\"]?", desc)
            if replace_match:
                old, new, directory = replace_match.groups()
                self.logger.info(f"Direct Execution: replace_text({directory}, {old}, {new})")
                return True, file_agent.replace_text(directory, old, new)

            # 3. RENAME / MOVE
            rename_match = re.search(r"rename\s+['\"]?([^'\s]+)['\"]?\s+to\s+['\"]?([^'\s]+)['\"]?", desc)
            if rename_match:
                old, new = rename_match.groups()
                self.logger.info(f"Direct Execution: rename_files('.', {old}, {new})")
                return True, file_agent.rename_files(".", old, new)

        except Exception as e:
            self.logger.error(f"Direct file execution failed: {e}")
        
        return False, {}

    def _detect_step_type(self, step: TaskStep) -> Tuple[str, str]:
        desc = step.description.lower()
        if any(kw in desc for kw in ["copy", "move", "rename", "delete", "branding", "replace text", "asset"]):
            return "file", "file_operation"
        if any(kw in desc for kw in ["run", "install", "npm", "pip", "execute", "setup"]):
            return "shell", "system_command"
        return "builder", "code_generation"

    def _verify_step(self, step: TaskStep, result: Dict[str, Any]) -> bool:
        v_result = self.verifier.run_empirical_check(self._detect_step_type(step)[1], {
            "required_files": step.required_files,
            "description": step.description
        })
        return v_result["success"]

    def _trigger_debug(self, step: TaskStep, error: str):
        debug_msg = Message(sender="execution_engine", receiver="debug", content={
            "action": "diagnose_and_fix",
            "error_msg": error,
            "step_description": step.description
        }, task_id=step.id)
        self.agent_manager.route_message(debug_msg)

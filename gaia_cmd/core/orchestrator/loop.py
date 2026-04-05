import os
import logging
import time
import re
from typing import Any, Dict, List, Optional
from gaia_cmd.core.llm.manager import LLMManager
from gaia_cmd.core.config.config import GaiaConfig
from gaia_cmd.tools.executor.executor import ToolExecutor
from gaia_cmd.core.debugging.engine import DebugEngine
from gaia_cmd.core.memory.manager import MemoryManager
from gaia_cmd.core.prompt.manager import PromptOrchestrator, PromptMode
from gaia_cmd.core.ui.cli import GaiaUI
from gaia_cmd.core.planning.models import ExecutionPlan, TaskStep, StepStatus
from gaia_cmd.core.orchestrator.checkpoint import CheckpointManager
from gaia_cmd.core.templates.manager import TemplateManager
from gaia_cmd.core.execution.parallel import ParallelExecutionEngine
from gaia_cmd.core.intelligence.task_classifier import TaskClassifier, TaskType
from gaia_cmd.core.execution.engine import PlanExecutionEngine

# Agent Imports
from gaia_cmd.core.communication.message import Message
from gaia_cmd.agents.planner.planner import PlannerAgent
from gaia_cmd.agents.builder.builder import BuilderAgent
from gaia_cmd.agents.debug.debug import DebugAgent
from gaia_cmd.agents.reviewer.reviewer import ReviewerAgent
from gaia_cmd.agents.memory.memory import MemoryAgent
from gaia_cmd.agents.system.upgrade_agent import UpgradeAgent
from gaia_cmd.agents.file.file_agent import FileAgent
from gaia_cmd.agents.shell.shell_agent import ShellAgent
from gaia_cmd.core.agents.manager import AgentManager
from gaia_cmd.core.prompt.role_config import AgentRole

# Configure Logging
logging.basicConfig(
    level=logging.ERROR,
    filename="gaia_internal.log",
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class GaiaOrchestrator:
    """
    Multi-Agent orchestrator for Gaia CLI.
    Supports Parallel Execution, Intelligent Task Classification, and Fast-Path deterministic edits.
    """
    def __init__(self, workspace_root: str, ui: Optional[GaiaUI] = None, forced_model: Optional[str] = None):
        self.workspace_root = workspace_root
        self.ui = ui or GaiaUI()
        
        # 1. Initialize Core Components
        self.config = GaiaConfig(workspace_root)
        self.llm_manager = LLMManager(self.config)
        if forced_model:
            self.llm_manager.set_forced_provider(forced_model)
            
        self.executor = ToolExecutor(workspace_root)
        self.classifier = TaskClassifier(self.llm_manager)
        self.debug_engine = DebugEngine(workspace_root, self.llm_manager)
        self.memory = MemoryManager(workspace_root)
        self.prompt_engine = PromptOrchestrator(workspace_root, self.memory, self.executor)
        self.checkpoint_manager = CheckpointManager(workspace_root)
        self.parallel_engine = ParallelExecutionEngine(max_workers=4)
        
        # 2. Initialize and Register Agents (Registry Style)
        self.agent_manager = AgentManager()
        
        # Register Core Agents
        self.agent_manager.register("planner", PlannerAgent(self.llm_manager))
        self.agent_manager.register("builder", BuilderAgent(self.llm_manager, self.executor, self.prompt_engine))
        self.agent_manager.register("code", self.agent_manager.get("builder")) # Alias
        self.agent_manager.register("file", FileAgent(self.llm_manager, self.executor, self.prompt_engine))
        self.agent_manager.register("shell", ShellAgent(self.llm_manager, self.executor, self.prompt_engine))
        self.agent_manager.register("debug", DebugAgent(self.llm_manager, self.debug_engine))
        self.agent_manager.register("reviewer", ReviewerAgent(self.llm_manager))
        self.agent_manager.register("memory", MemoryAgent(self.memory))
        self.agent_manager.register("system_upgrader", UpgradeAgent(self.llm_manager, workspace_root))

        # 3. Initialize Execution Engine (Injected with agent_manager)
        self.execution_engine = PlanExecutionEngine(self.agent_manager, self.ui, workspace_root)
        
        # 4. Initialize Template System
        templates_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../templates"))
        self.template_manager = TemplateManager(templates_path, self.llm_manager)
        
        self.logger = logging.getLogger("GaiaOrchestrator")
        self.current_plan: Optional[ExecutionPlan] = None
        self.session_context: Dict[str, Any] = {
            "workspace_root": workspace_root,
            "model": forced_model or "qwen2.5-coder:7b" # Consistent internal ID
        }

    def run(self, user_goal: str):
        """Executes a goal with intelligent classification and routing."""
        
        # 0. Fast-Path Deterministic Edits (Instant execution for simple tasks)
        if self._try_fast_path_edit(user_goal):
            return True

        # 1. Task Classification
        self.ui.show_thinking("Perceiving intent")
        classification = self.classifier.classify_task(user_goal)
        task_type = classification["type"]
        confidence = classification["confidence"]
        
        self.logger.info(f"Task Classified: {task_type} (Confidence: {confidence})")
        
        # 2. Inform user of classification if slightly uncertain, but always proceed
        if confidence < 0.7:
            self.ui.show_manifestation("realigning", f"Proceeding with inferred intent: {task_type}")
            self.logger.info(f"Low confidence ({confidence:.2f}), proceeding with fallback: {task_type}")

        # Route specific single-agent tasks if they don't need a full plan
        if task_type == TaskType.FILE_OPERATION.value and "multi" not in user_goal.lower():
            return self._run_single_agent("file", user_goal)
        elif task_type == TaskType.SYSTEM_COMMAND.value and "build" not in user_goal.lower():
            return self._run_single_agent("shell", user_goal)

        # Proceed with standard multi-agent planning
        return self._run_full_orchestration(user_goal)

    def _try_fast_path_edit(self, goal: str) -> bool:
        """
        Detects simple, deterministic file modification tasks and executes them instantly.
        Bypasses LLM and Planner for high-speed routine edits.
        """
        g = goal.lower()
        
        # Pattern 1: Dark Mode Injection
        if "dark mode" in g and any(ext in g for ext in [".html", ".css", ".js", "style", "theme"]):
            self.ui.show_thinking("Applying instant dark mode")
            dark_css = "\n/* Gaia Instant Dark Mode */\nbody { background-color: #121212 !important; color: #ffffff !important; }\n"
            
            # Find CSS files
            css_found = False
            for root, _, files in os.walk(self.workspace_root):
                for f in files:
                    if f.endswith(".css"):
                        path = os.path.relpath(os.path.join(root, f), self.workspace_root)
                        current = self.executor.execute_tool("read_file", {"path": path})
                        if current.get("status") == "success":
                            self.executor.execute_tool("write_file", {"path": path, "content": current["output"] + dark_css})
                            self.ui.show_manifestation("evolved", f"Injected dark theme into {path}")
                            css_found = True
            
            if css_found:
                self.ui.show_success("Substrate harmonized with dark mode.")
                return True

        # Pattern 2: Explicit Color Change
        color_match = re.search(r"change color (?:of|in) ([\w\.\/-]+) to ([\w#]+)", g)
        if color_match:
            file_path, color = color_match.groups()
            self.ui.show_thinking(f"Adjusting chromatic profile of {file_path}")
            # Logic: simplistic replace for common color keywords or hex
            # This is a basic example of deterministic substitution
            current = self.executor.execute_tool("read_file", {"path": file_path})
            if current.get("status") == "success":
                # Very simple regex to find color-like assignments
                content = current["output"]
                new_content = re.sub(r"(color:\s*)([\w#]+)", f"\\1{color}", content)
                if new_content != content:
                    self.executor.execute_tool("write_file", {"path": file_path, "content": new_content})
                    self.ui.show_success(f"Chromatic shift complete for {file_path}.")
                    return True

        return False

    def _run_single_agent(self, agent_name: str, goal: str) -> bool:
        """Optimized path for simple tasks routed to a specific agent."""
        self.ui.show_manifestation("evolved", f"Routing directly to {agent_name.capitalize()} Agent")
        
        msg = Message(sender="orchestrator", receiver=agent_name, content={
            "action": "execute_step",
            "description": goal,
            "goal": "Direct execution complete"
        })
        response = self.agent_manager.route_message(msg)
        
        if response.content.get("success"):
            self.ui.show_success(goal)
            return True
        else:
            self.ui.show_error(f"Execution failed: {response.content.get('error')}")
            return False

    def _run_full_orchestration(self, user_goal: str):
        """Standard multi-step orchestration path."""
        # Special cases (PLAN ONLY, BUILD, SYSTEM)
        if user_goal.upper().startswith("PLAN ONLY:"):
            user_goal = user_goal[10:].strip()
            
        if user_goal.upper().startswith("SYSTEM:"):
            self.ui.show_thinking("Executing system maintenance")
            return True

        if user_goal.upper().startswith("BUILD:"):
            return self._handle_template_build(user_goal[6:].strip())

        # 3. Checkpoint Management
        is_resume_request = user_goal.lower().strip() == "resume last task"
        
        if is_resume_request:
            self.current_plan = self.checkpoint_manager.load_checkpoint()
            if self.current_plan:
                self.ui.show_manifestation("evolved", "Resuming from checkpoint...")
                if self.current_plan.design:
                    self.ui.show_design(self.current_plan.design.to_dict())
                self.ui.show_plan(list(self.current_plan.to_dict()["steps"]))
            else:
                self.ui.show_error("No active checkpoint found to resume.")
                return False
        else:
            # New task received: CLEAR previous state to ensure a fresh start
            self.checkpoint_manager.clear_checkpoint()
            self.current_plan = None

        if not self.current_plan:
            # Planning Phase for New Task
            self.ui.show_thinking("Synthesizing architecture (Planner Agent)")
            prompt_payload = self.prompt_engine.get_task_payload(user_goal, mode=PromptMode.ARCHITECTURE, agent_role=AgentRole.PLANNER)
            
            msg = Message(sender="orchestrator", receiver="planner", content={
                "action": "create_plan",
                "goal": user_goal,
                "context": {"prompt": prompt_payload}
            })
            response = self.agent_manager.route_message(msg)
            
            if "plan" in response.content:
                self.current_plan = response.content["plan"]
                if self.current_plan.design:
                    self.ui.show_design(self.current_plan.design.to_dict())
                self.ui.show_plan(list(self.current_plan.to_dict()["steps"]))
                self.checkpoint_manager.save_checkpoint(self.current_plan)
            else:
                self.ui.show_error(f"Planning failed: {response.content.get('error')}")
                return False

        # Main Loop
        while not self.current_plan.is_complete():
            runnable_steps = self.current_plan.get_next_runnable_steps()
            if not runnable_steps:
                break
            
            if len(runnable_steps) > 1:
                self.parallel_engine.execute_in_parallel(runnable_steps, self._execute_step_via_agents)
            else:
                success = self.execution_engine.execute_step(runnable_steps[0], {
                    "memory": self.session_context,
                    "model": self.session_context.get("model")
                })
                if not success:
                    self._handle_step_failure(runnable_steps[0])
            
            self.checkpoint_manager.save_checkpoint(self.current_plan)

        self.ui.show_success(user_goal)
        self.checkpoint_manager.clear_checkpoint()
        return True

    def _handle_template_build(self, build_goal: str) -> bool:
        template = self.template_manager.match_template(build_goal)
        if template:
            self.ui.show_manifestation("evolved", f"Found template: {template['name']}")
            files = self.template_manager.get_template_files(template["id"])
            files = self.template_manager.customize_template(files, build_goal)
            for path, content in files.items():
                self.executor.execute_tool("write_file", {"path": path, "content": content})
                self.ui.show_manifestation("manifested", path)
            self.ui.show_success(f"Initialized {template['name']}.")
            return True
        return False

    def _handle_step_failure(self, step: TaskStep):
        self.ui.show_manifestation("realigning", f"Step {step.id} failed. Triggering recovery.")
        mem_resp = self.agent_manager.route_message(Message("orchestrator", "memory", {"action": "get_context"}))
        replan_resp = self.agent_manager.route_message(Message("orchestrator", "planner", {
            "action": "replan",
            "current_plan": self.current_plan,
            "current_state": mem_resp.content.get("context", {}),
            "failure_report": f"Step '{step.id}' failed."
        }))
        if "plan" in replan_resp.content:
            self.current_plan = replan_resp.content["plan"]
            self.ui.show_manifestation("evolved", "Strategy revised.")

    def _execute_step_via_agents(self, step: TaskStep, max_retries: int = 5) -> bool:
        """Fallback helper for parallel execution."""
        return self.execution_engine.execute_step(step, {"memory": self.session_context}, max_retries)

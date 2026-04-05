import logging
from typing import Dict, Optional
from gaia_cmd.agents.base import BaseAgent
from gaia_cmd.agents.planner.planner import PlannerAgent
from gaia_cmd.agents.builder.builder import BuilderAgent
from gaia_cmd.agents.debug.debug import DebugAgent
from gaia_cmd.agents.reviewer.reviewer import ReviewerAgent
from gaia_cmd.agents.memory.memory import MemoryAgent
from gaia_cmd.agents.system.upgrade_agent import UpgradeAgent
from gaia_cmd.agents.file.file_agent import FileAgent
from gaia_cmd.agents.shell.shell_agent import ShellAgent
from gaia_cmd.core.communication.message import Message

class AgentManager:
    """
    Central hub for managing agents and routing messages.
    Now includes specialized File and Shell agents.
    """
    def __init__(self, planner: PlannerAgent, builder: BuilderAgent, 
                 debug: DebugAgent, reviewer: ReviewerAgent, memory: MemoryAgent,
                 file_agent: FileAgent, shell_agent: ShellAgent,
                 upgrader: Optional[UpgradeAgent] = None):
        self.agents: Dict[str, BaseAgent] = {
            planner.name: planner,
            builder.name: builder,
            debug.name: debug,
            reviewer.name: reviewer,
            memory.name: memory,
            file_agent.name: file_agent,
            shell_agent.name: shell_agent
        }
        if upgrader:
            self.agents[upgrader.name] = upgrader
            
        self.logger = logging.getLogger("AgentManager")

    def route_message(self, message: Message) -> Message:
        """
        Routes a message to the appropriate agent and returns the response.
        """
        self.logger.info(f"Routing message from {message.sender} to {message.receiver}")
        
        receiver_agent = self.agents.get(message.receiver)
        if not receiver_agent:
            error_msg = f"Agent '{message.receiver}' not found."
            self.logger.error(error_msg)
            return Message(
                sender="system",
                receiver=message.sender,
                content={"success": False, "error": error_msg},
                task_id=message.task_id
            )
            
        try:
            return receiver_agent.process_message(message)
        except Exception as e:
            self.logger.error(f"Error processing message in {message.receiver}: {e}")
            return Message(
                sender="system",
                receiver=message.sender,
                content={"success": False, "error": str(e)},
                task_id=message.task_id
            )

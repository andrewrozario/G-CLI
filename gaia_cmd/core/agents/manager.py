import logging
from typing import Dict, Any, Optional

class AgentManager:
    """
    Central registry for managing agents and routing messages.
    """
    def __init__(self):
        self.agents: Dict[str, Any] = {}
        self.logger = logging.getLogger("AgentManager")

    def register(self, name: str, agent: Any):
        """Registers an agent with a unique name."""
        self.agents[name] = agent
        self.logger.info(f"Agent '{name}' registered successfully.")

    def get(self, name: str) -> Optional[Any]:
        """Retrieves a registered agent by name."""
        return self.agents.get(name)

    def route_message(self, message: Any) -> Any:
        """
        Helper to maintain compatibility with the existing message-based routing.
        """
        receiver_name = message.receiver
        agent = self.get(receiver_name)
        if not agent:
            # Fallback for generic 'builder' or 'code' mapping
            if receiver_name in ["builder", "code"]:
                agent = self.get("builder") or self.get("code")
            elif receiver_name == "file_agent":
                agent = self.get("file")
            elif receiver_name == "shell_agent":
                agent = self.get("shell")
        
        if agent and hasattr(agent, 'process_message'):
            return agent.process_message(message)
        
        # Return an error message or raise exception
        from gaia_cmd.core.communication.message import Message
        return Message(
            sender="system",
            receiver=message.sender,
            content={"success": False, "error": f"Agent '{receiver_name}' not found or inactive."},
            task_id=message.task_id
        )

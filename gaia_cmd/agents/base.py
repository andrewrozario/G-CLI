from abc import ABC, abstractmethod
from typing import Optional, Any
import logging
from gaia_cmd.core.communication.message import Message

class BaseAgent(ABC):
    """
    Abstract base class for all Gaia CLI agents.
    """
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"Agent.{self.name}")

    @abstractmethod
    def process_message(self, message: Message) -> Message:
        """
        Process an incoming message and return a response message.
        """
        pass

    def send_message(self, receiver: str, content: Any, task_id: Optional[str] = None, metadata: Optional[dict] = None) -> Message:
        """
        Helper to construct a message to another agent.
        """
        return Message(
            sender=self.name,
            receiver=receiver,
            content=content,
            task_id=task_id,
            metadata=metadata or {}
        )

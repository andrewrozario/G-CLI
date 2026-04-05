from dataclasses import dataclass, field
from typing import Any, Dict, Optional
import time
import uuid

@dataclass
class Message:
    """
    Structured message for inter-agent communication.
    """
    sender: str
    receiver: str
    content: Any
    task_id: Optional[str] = None
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "sender": self.sender,
            "receiver": self.receiver,
            "content": self.content,
            "task_id": self.task_id,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }

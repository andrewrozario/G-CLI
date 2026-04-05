import os
import json
import logging
from typing import Dict, Any, Optional
from gaia_cmd.core.planning.models import ExecutionPlan

class CheckpointManager:
    """
    Handles saving and restoring the execution state of the agent loop.
    Enables resuming interrupted tasks.
    """
    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root
        self.logger = logging.getLogger("CheckpointManager")
        self.checkpoint_dir = os.path.join(workspace_root, "memory", "checkpoints")
        self.checkpoint_file = os.path.join(self.checkpoint_dir, "current_plan.json")
        self._ensure_dir()

    def _ensure_dir(self):
        os.makedirs(self.checkpoint_dir, exist_ok=True)

    def save_checkpoint(self, plan: ExecutionPlan):
        """Saves the current execution plan to disk."""
        try:
            with open(self.checkpoint_file, "w") as f:
                json.dump(plan.to_dict(), f, indent=4)
            self.logger.debug("Checkpoint saved successfully.")
        except Exception as e:
            self.logger.error(f"Failed to save checkpoint: {e}")

    def load_checkpoint(self) -> Optional[ExecutionPlan]:
        """Loads the execution plan from disk if it exists and is incomplete."""
        if not os.path.exists(self.checkpoint_file):
            return None
            
        try:
            with open(self.checkpoint_file, "r") as f:
                data = json.load(f)
            
            plan = ExecutionPlan.from_dict(data)
            if plan.is_complete():
                self.logger.debug("Existing checkpoint is already complete. Ignoring.")
                self.clear_checkpoint()
                return None
                
            self.logger.info("Found active checkpoint. Resuming plan.")
            return plan
        except Exception as e:
            self.logger.error(f"Failed to load checkpoint: {e}")
            return None

    def clear_checkpoint(self):
        """Removes the checkpoint file once a goal is fully complete."""
        if os.path.exists(self.checkpoint_file):
            try:
                os.remove(self.checkpoint_file)
                self.logger.debug("Checkpoint cleared.")
            except Exception as e:
                self.logger.error(f"Failed to clear checkpoint: {e}")

    def has_active_checkpoint(self) -> bool:
        """Checks if a valid, incomplete checkpoint exists."""
        plan = self.load_checkpoint()
        return plan is not None

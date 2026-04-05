import os
import shutil
import logging
import time
from typing import Dict, Any, List, Optional
from gaia_cmd.core.system.versioning import VersionManager

class UpgradeManager:
    """
    Handles the safe self-upgrade mechanism for Gaia CLI.
    Supports backups, rollbacks, and atomic file swaps.
    """
    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root
        self.version_manager = VersionManager(workspace_root)
        self.backup_dir = os.path.join(workspace_root, "memory", "backups", "system")
        self.logger = logging.getLogger("UpgradeManager")
        os.makedirs(self.backup_dir, exist_ok=True)

    def prepare_upgrade(self, module_path: str) -> str:
        """Creates a backup of the module before upgrading."""
        timestamp = int(time.time())
        module_name = os.path.basename(module_path)
        backup_path = os.path.join(self.backup_dir, f"{module_name}.{timestamp}.bak")
        
        full_source = os.path.join(self.workspace_root, module_path)
        if os.path.exists(full_source):
            if os.path.isdir(full_source):
                shutil.copytree(full_source, backup_path)
            else:
                shutil.copy2(full_source, backup_path)
            self.logger.info(f"Backup created at {backup_path}")
            return backup_path
        return ""

    def apply_patch(self, module_path: str, new_content: str) -> bool:
        """Applies a code patch to a specific file."""
        full_path = os.path.join(self.workspace_root, module_path)
        try:
            # Atomic-ish write
            temp_path = full_path + ".tmp"
            with open(temp_path, 'w') as f:
                f.write(new_content)
            
            os.replace(temp_path, full_path)
            self.logger.info(f"Applied patch to {module_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to apply patch to {module_path}: {e}")
            return False

    def finalize_upgrade(self):
        """Updates the system version after a successful upgrade batch."""
        new_version = self.version_manager.increment_patch()
        self.version_manager.update_version(new_version)
        return new_version

    def rollback(self, module_path: str, backup_path: str) -> bool:
        """Restores a module from a backup if an upgrade fails."""
        full_path = os.path.join(self.workspace_root, module_path)
        try:
            if os.path.exists(full_path):
                if os.path.isdir(full_path):
                    shutil.rmtree(full_path)
                else:
                    os.remove(full_path)
            
            if os.path.isdir(backup_path):
                shutil.copytree(backup_path, full_path)
            else:
                shutil.copy2(backup_path, full_path)
            
            self.logger.info(f"Rolled back {module_path} from {backup_path}")
            return True
        except Exception as e:
            self.logger.error(f"Rollback failed for {module_path}: {e}")
            return False

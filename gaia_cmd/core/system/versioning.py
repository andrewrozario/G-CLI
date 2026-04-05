import os
import logging

class VersionManager:
    """
    Manages Gaia CLI versioning and consistency checks.
    """
    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root
        self.version_file = os.path.join(workspace_root, "VERSION")
        self.logger = logging.getLogger("VersionManager")

    def get_current_version(self) -> str:
        """Reads the current version from the VERSION file."""
        try:
            if os.path.exists(self.version_file):
                with open(self.version_file, 'r') as f:
                    return f.read().strip()
            return "0.0.0"
        except Exception as e:
            self.logger.error(f"Failed to read version: {e}")
            return "unknown"

    def update_version(self, new_version: str):
        """Updates the VERSION file."""
        try:
            with open(self.version_file, 'w') as f:
                f.write(new_version)
            self.logger.info(f"Gaia CLI upgraded to version {new_version}")
        except Exception as e:
            self.logger.error(f"Failed to update version file: {e}")

    def increment_patch(self) -> str:
        """Increments the patch version (e.g., 1.0.0 -> 1.0.1)."""
        current = self.get_current_version()
        try:
            parts = current.split('.')
            if len(parts) == 3:
                parts[2] = str(int(parts[2]) + 1)
                new_version = '.'.join(parts)
                return new_version
        except:
            pass
        return current

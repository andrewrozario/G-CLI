import os

class ProjectScanner:
    """Recursively scans a project directory to provide G CLI with system-wide vision."""
    def __init__(self, ignore_dirs=None):
        self.ignore_dirs = ignore_dirs or ['.git', '__pycache__', 'node_modules', 'venv', '.gaia_memory']

    def scan(self, root_dir: str) -> list:
        file_list = []
        for root, dirs, files in os.walk(root_dir):
            # Prune ignored directories
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs]
            for file in files:
                file_list.append(os.path.join(root, file))
        return file_list

import os
import psutil

class SystemState:
    """Monitors OS-level resources and environmental context."""
    
    def get_snapshot(self) -> dict:
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "ram_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "cwd": os.getcwd()
        }

    def format_snapshot(self) -> str:
        snap = self.get_snapshot()
        return f"[System State] CPU: {snap['cpu_percent']}%, RAM: {snap['ram_percent']}%, Disk: {snap['disk_percent']}%, CWD: {snap['cwd']}"

import os
from system.command_runner import CommandRunner
from rich.console import Console

class GitClient:
    """Integrates G CLI with the local Git workflow."""
    def __init__(self):
        self.runner = CommandRunner()
        self.console = Console()

    def is_repo(self) -> bool:
        return os.path.exists(".git")

    def commit(self, file_path: str, message: str):
        if not self.is_repo():
            return
        
        self.runner.run(f"git add {file_path}")
        res = self.runner.run(f"git commit -m \"{message}\"")
        if res["success"]:
            self.console.print(f"📦 [bold green]Changes committed to Git:[/bold green] {message}")
        else:
            self.console.print("[dim]Git commit skipped (likely no changes or not a repo).[/dim]")

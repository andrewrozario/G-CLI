import os
from .file_watcher import FileWatcher
from .change_analyzer import ChangeAnalyzer
from rich.console import Console

class ContinuousMode:
    """The engine that connects real-time file changes to AI analysis."""
    def __init__(self, orchestrator, auto_fix: bool = False):
        self.orchestrator = orchestrator
        self.auto_fix = auto_fix
        self.analyzer = ChangeAnalyzer()
        self.console = Console()

    def run(self, project_path: str):
        watcher = FileWatcher(project_path, self._handle_change)
        watcher.start()

    def _handle_change(self, file_path: str):
        self.console.print(f"\n📂 [bold cyan]File changed:[/bold cyan] {os.path.basename(file_path)}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        issues = self.analyzer.analyze(file_path, content)
        if issues:
            self.console.print(f"🧠 [bold yellow]G noticed issues:[/bold yellow]")
            for issue in issues:
                self.console.print(f"   • {issue}")

        # Trigger multi-model analysis
        objective = f"Analyze recent changes in {file_path} and suggest or apply improvements."
        
        # In watcher mode, we usually want to be less intrusive unless --auto is passed
        if self.auto_fix:
            self.orchestrator.execute(objective, force=False)
        else:
            self.orchestrator.execute(objective, preview=True)
            self.console.print(f"🔧 [dim]Suggested fixes prepared for {os.path.basename(file_path)}[/dim]")

from .test_runner import TestRunner
from .error_parser import ErrorParser
from .self_healer import SelfHealer
from rich.console import Console

class HealingLoop:
    """Orchestrates the verify-detect-fix loop to ensure code stability."""
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.test_runner = TestRunner()
        self.error_parser = ErrorParser()
        self.healer = SelfHealer()
        self.console = Console()

    def heal(self, file_path: str, current_content: str, max_attempts: int = 3) -> str:
        for i in range(max_attempts):
            test_result = self.test_runner.run()
            
            if test_result["success"]:
                self.console.print("✅ [bold green]System stable. Tests passed.[/bold green]")
                return current_content
            
            self.console.print(f"❌ [bold red]Breakage detected (Attempt {i+1}/{max_attempts})[/bold red]")
            errors = self.error_parser.parse(test_result["output"])
            
            if not errors:
                self.console.print("⚠️ [bold yellow]Unknown failure. Aborting self-heal.[/bold yellow]")
                break
                
            # Attempt fix
            self.console.print("🛠 [bold cyan]Attempting auto-fix with Codex...[/bold cyan]")
            fix_output = self.healer.fix(errors, current_content, file_path)
            
            # Apply fix (temporarily overwrite to test)
            self.orchestrator.file_manager.write_file(file_path, fix_output, backup=False)
            current_content = fix_output
            
        self.console.print("❌ [bold red]Self-healing failed to stabilize after multiple attempts.[/bold red]")
        return current_content

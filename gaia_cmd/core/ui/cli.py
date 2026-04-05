import sys
import time
from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.table import Table
from rich.spinner import Spinner
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown
from gaia_cmd.ui.display import GaiaDisplay, console
from gaia_cmd.ui.streaming import GaiaStreamer

class GaiaUI:
    """
    The Visual Interface for Gaia CLI.
    Upgraded to use the premium Gaia Cyber-Organic design system.
    """
    def __init__(self):
        self.console = console
        self.display = GaiaDisplay()
        self.streamer = GaiaStreamer()

    def print_welcome(self):
        self.display.show_header()
        self.console.print("\n[italic grey50]Gaia is online. What shall we manifest today?[/]\n")

    def show_thinking(self, message: str):
        self.display.show_thinking(message)

    def show_design(self, design: Dict[str, Any]):
        if not design:
            return

        table = Table(title="[bold cyan]System Design Strategy[/bold cyan]", border_style="cyan", box=None)
        table.add_column("Category", style="bold white", width=20)
        table.add_column("Details", style="dim")

        table.add_row("Architecture", design.get("architecture_type", "modular"))
        table.add_row("Tech Stack", str(design.get("tech_stack", {})))
        
        components = design.get("components", [])
        comp_str = "\n".join([f"- {c.get('name')}: {c.get('purpose')}" for c in components])
        table.add_row("Components", comp_str)
        
        risks = design.get("risks", [])
        risk_str = "\n".join([f"- {r.get('risk')} (Mitigation: {r.get('mitigation')})" for r in risks])
        table.add_row("Risks", risk_str)
        
        self.display.show_panel(table, "Architectural Blueprint", style="gaia.cyan")
        
        if design.get("reasoning"):
            self.display.show_panel(design["reasoning"], "Design Reasoning", style="gaia.dim")

    def show_plan(self, plan: List[Dict[str, Any]]):
        table = Table(title="[bold cyan]Execution Roadmap[/bold cyan]", border_style="cyan")
        table.add_column("ID", style="dim", width=8)
        table.add_column("Task Description", style="white")
        table.add_column("Goal", style="dim")

        for task in plan:
            table.add_row(task.get("id", ""), task.get("description", ""), task.get("goal", ""))
        
        self.console.print(table)

    def show_manifestation(self, action: str, message: str):
        self.display.log_manifestation(action, message)

    def show_action(self, tool_name: str, params: Dict[str, Any]):
        self.console.print(f"[bold yellow]▶ Action:[/bold yellow] [cyan]{tool_name}[/cyan] with [dim]{params}[/dim]")

    def stream_output(self, text: str, prefix: str = "◉ GAIA > "):
        self.streamer.stream_text(text, prefix=prefix)

    def show_result(self, status: str, data: Any):
        if status == "success":
            self.show_manifestation("stabilized", "Outcome verified.")
        else:
            self.show_manifestation("realigning", str(data))

    def show_progress(self, current_task_num: int, total_tasks: int, task_name: str):
        self.console.rule(f"[bold blue]Sub-task {current_task_num}/{total_tasks}: {task_name}[/bold blue]")

    def show_learning(self, diagnosis: str):
        self.display.show_panel(diagnosis, "Neural Insight", style="gaia.gold")

    def show_success(self, goal: str):
        self.display.show_success(f"Objective Complete: {goal}")

    def show_error(self, message: str):
        self.display.show_error(message)

    def ask(self) -> str:
        return self.console.input("[gaia.prompt]◉ GAIA > [/]").strip()

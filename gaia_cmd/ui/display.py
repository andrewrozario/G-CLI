import os
from typing import Dict, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.columns import Columns
from rich.theme import Theme
from rich.align import Align

# Gaia Cyber-Organic Theme
GAIA_THEME = Theme({
    "gaia.green": "#2ECC71",
    "gaia.cyan": "#00E5FF",
    "gaia.gold": "#D4AF37",
    "gaia.dim": "#666666",
    "gaia.error": "#E74C3C",
    "gaia.prompt": "bold #00E5FF",
    "gaia.bg": "#0C0C0C"
})

console = Console(theme=GAIA_THEME)

class GaiaDisplay:
    @staticmethod
    def get_logo() -> str:
        logo_path = os.path.join(os.path.dirname(__file__), "..", "assets", "ascii_logo.txt")
        try:
            with open(logo_path, "r") as f:
                return f.read()
        except FileNotFoundError:
            return "G A I A"

    @staticmethod
    def show_header():
        logo = GaiaDisplay.get_logo()
        header_text = Text()
        header_text.append(logo, style="gaia.cyan")
        header_text.append("\n\nGAIA — Intelligent Systems Architect", style="bold gaia.green")
        header_text.append("\nv2.0.0 • Neural Architect Substrate", style="gaia.dim")
        header_text.justify = "center"
        
        panel = Panel(
            header_text, 
            border_style="gaia.cyan", 
            padding=(1, 2),
            expand=False
        )
        console.print(Align.center(panel))

    @staticmethod
    def show_status_bar(workspace: str, mode: str, model: str = "DeepSeek Code"):
        table = Table.grid(expand=True)
        table.add_column(justify="left", ratio=1)
        table.add_column(justify="center", ratio=1)
        table.add_column(justify="right", ratio=1)

        table.add_row(
            f"[gaia.dim]workspace:[/] [gaia.cyan]{workspace}[/]",
            f"[gaia.dim]mode:[/] [gaia.gold]{mode.upper()}[/]",
            f"[gaia.dim]model:[/] [gaia.green]{model}[/]"
        )
        console.print(Panel(table, border_style="gaia.dim", padding=(0, 1)))

    @staticmethod
    def show_thinking(message: str):
        console.print(f"\n[gaia.dim]⠋ {message}...[/]")

    @staticmethod
    def log_manifestation(action: str, message: str):
        """
        Styled manifestation logs.
        - action: 'manifested' (green), 'evolved' (yellow), 'realigning' (red), 'stabilized' (cyan)
        """
        styles = {
            "manifested": ("✦", "gaia.green", "Manifested"),
            "evolved": ("↺", "gaia.gold", "Evolved"),
            "realigning": ("⚠", "gaia.error", "Realigning"),
            "stabilized": ("✓", "gaia.cyan", "Stabilized")
        }
        icon, style, label = styles.get(action.lower(), ("•", "white", action.capitalize()))
        console.print(f"  [{style}]{icon} {label}:[/] [white]{message}[/]")

    @staticmethod
    def show_error(message: str):
        console.print(Panel(f"[gaia.error]{message}[/]", title="[gaia.error]⚠ Error[/]", border_style="gaia.error"))

    @staticmethod
    def show_success(message: str):
        console.print(Panel(f"[gaia.green]{message}[/]", title="[gaia.green]✓ Success[/]", border_style="gaia.green"))

    @staticmethod
    def show_panel(content: Any, title: str, style: str = "gaia.cyan"):
        console.print(Panel(content, title=f"[{style}]{title}[/]", border_style="gaia.dim", padding=(1, 2)))

#!/usr/bin/env python3
import sys
import os
import warnings

# Suppress Pydantic and LangChain deprecation warnings for high-fidelity UI
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")
warnings.filterwarnings("ignore", category=UserWarning, module="langchain_core")

# Add the project root to sys.path to allow global imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import typer
from rich.console import Console
from rich.panel import Panel
from core.brain.centralOrchestrator import CentralOrchestrator
from core.meta.orchestrator import MetaOrchestrator # v2 legacy fallback
from dotenv import load_dotenv

load_dotenv()

app = typer.Typer(help="Gaia v3: Autonomous AI Operating System")
console = Console()

from core.personality.ux_elements import ASCII_ART, get_random_subtitle
from rich.live import Live
from rich.text import Text

# Global orchestrator instance
_v3_brain = None

def show_boot_screen():
    console.print(f"[bold cyan]{ASCII_ART}[/bold cyan]")
    console.print(f"      [bold white]G  C  L  I[/bold white]")
    console.print(f"  [italic dim]\"{get_random_subtitle()}\"[/italic dim]\n")

def get_v3_brain():
    global _v3_brain
    if _v3_brain is None:
        _v3_brain = CentralOrchestrator()
    return _v3_brain

@app.command()
def watch(
    path: str = typer.Argument(".", help="Project path to watch"),
    auto: bool = typer.Option(False, "--auto", help="Auto-fix small issues detected during watch"),
    safe: bool = typer.Option(True, "--safe", help="Only show previews, never auto-write")
):
    """Start G CLI Continuous Mode: G watches, thinks, and prepares as you work."""
    show_boot_screen()
    from core.watcher.continuous_mode import ContinuousMode
    orchestrator = MetaOrchestrator()
    
    watcher = ContinuousMode(orchestrator, auto_fix=auto and not safe)
    try:
        watcher.run(os.path.abspath(path))
    except KeyboardInterrupt:
        console.print("\n[bold cyan]G CLI Continuous Mode Deactivated.[/bold cyan]")

@app.command()
def ask(
    objective: str, 
    mode: str = typer.Option("deep", help="Execution mode: 'fast' or 'deep'"), 
    chain_debug: bool = typer.Option(False, "--chain-debug", help="Show cognitive strategy trace"),
    claude: bool = typer.Option(False, "--claude", help="Force Claude (Architect) brain"),
    codex: bool = typer.Option(False, "--codex", help="Force Codex (Engineer) brain"),
    gemini: bool = typer.Option(False, "--gemini", help="Force Gemini (Observer) brain"),
    force: bool = typer.Option(False, "--force", "-f", help="Force apply changes without confirmation"),
    preview: bool = typer.Option(False, "--preview", "-p", help="Show changes only, do not apply"),
    verbose: bool = False
):
    """Execute a task using G CLI's integrated intelligence."""
    show_boot_screen()
    orchestrator = MetaOrchestrator()
    
    # Direct brain override
    if claude:
        orchestrator.execute(objective, mode="fast", force_model="claude", force=force, preview=preview)
    elif codex:
        orchestrator.execute(objective, mode="fast", force_model="codex", force=force, preview=preview)
    elif gemini:
        orchestrator.execute(objective, mode="fast", force_model="gemini", force=force, preview=preview)
    else:
        orchestrator.execute(objective, mode=mode, chain_debug=chain_debug, force=force, preview=preview)

@app.command()
def chat(mode: str = "deep", force: bool = False, preview: bool = False, verbose: bool = False):
    """Enter G CLI's Cognitive Environment."""
    orchestrator = MetaOrchestrator()
    console.print(f"[bold cyan]{ASCII_ART}[/bold cyan]")
    orchestrator.show_workspace_dashboard()
    console.print("[dim]Gaia is synchronized. Type 'exit' to disconnect.[/dim]\n")
    while True:
        try:
            # Idle symbol: G •
            user_input = typer.prompt("G • ")
            if user_input.lower() in ["exit", "quit"]: 
                break
            
            # Undo logic
            if user_input.lower().startswith("undo "):
                from core.utils.undo_system import undo_last_change
                path = user_input.split(" ", 1)[1].strip()
                undo_last_change(path)
                continue

            # Execution will handle the thinking symbol
            orchestrator.execute(user_input, mode=mode, force=force, preview=preview)
        except KeyboardInterrupt:
            break

@app.command()
def doctor():
    """Diagnose G CLI health, dependencies, and API connections."""
    console.print("\n👨‍⚕️ [bold cyan]G CLI System Check[/bold cyan]\n")
    
    # Check Python Version
    import platform
    console.print(f"• Python: {platform.python_version()} ([green]OK[/green])")
    
    # Check API Keys
    from core.meta.orchestrator import MetaOrchestrator
    orch = MetaOrchestrator()
    orch.validate_api_keys()
    
    # Check Git
    import subprocess
    git_res = subprocess.run("git --version", shell=True, capture_output=True)
    if git_res.returncode == 0:
        console.print(f"• Git: Found ([green]OK[/green])")
    else:
        console.print(f"• Git: [red]Not found[/red] (Git integration disabled)")

    console.print("\n✅ [bold green]Diagnosis complete.[/bold green]")

@app.command()
def config(
    claude: str = typer.Option(None, help="Set Claude API Key"),
    gemini: str = typer.Option(None, help="Set Gemini API Key"),
    codex: str = typer.Option(None, help="Set Codex/OpenAI API Key")
):
    """Configure G CLI API keys and settings."""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    
    current_env = {}
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    current_env[k] = v

    if claude: current_env["ANTHROPIC_API_KEY"] = claude
    if gemini: current_env["GEMINI_API_KEY"] = gemini
    if codex: current_env["OPENAI_API_KEY"] = codex

    with open(env_path, 'w') as f:
        for k, v in current_env.items():
            f.write(f"{k}={v}\n")
    
    console.print("⚙️ [bold green]Configuration updated successfully.[/bold green]")

@app.command()
def update():
    """Pull the latest intelligence and system updates."""
    console.print("🚀 [bold cyan]Updating G CLI...[/bold cyan]")
    import subprocess
    subprocess.run("git pull", shell=True)
    subprocess.run("pip install -e . --break-system-packages --user", shell=True)
    console.print("✨ [bold green]G CLI is now up to date.[/bold green]")

@app.command()
def status():
    """Display system state and health."""
    brain = get_v3_brain()
    # ... (rest of status)
    console.print(f"Active Goals: {len(brain.goals.get_active_goals())}")
    # Show system stats via v2 bridge (integrated)
    from core.gaia.systemState import SystemState
    console.print(SystemState().format_snapshot())

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Default behavior: enter chat mode if no command is provided."""
    if ctx.invoked_subcommand is None:
        chat()

if __name__ == "__main__":
    console.print("[bold blue][BOOT][/bold blue] G CLI v3 Initialized")
    try:
        app()
    except Exception as e:
        console.print(f"[bold red][ERROR][/bold red] G CLI encountered a critical error: {e}")
        import traceback
        # console.print(traceback.format_exc()) # Optional: show stack trace

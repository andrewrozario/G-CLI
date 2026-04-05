import typer
import os
from rich.console import Console
from rich.panel import Panel
from core.orchestrator import GCLI_Orchestrator
from dotenv import load_dotenv

load_dotenv()

app = typer.Typer(help="G CLI v2: The Multi-Model Intelligence Brain")
console = Console()

# Global orchestrator instance
_orchestrator = None

def get_orchestrator():
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = GCLI_Orchestrator()
    return _orchestrator

@app.command()
def run(objective: str, collaborate: bool = True, verbose: bool = True):
    """Execute a task using the multi-model G CLI Brain."""
    orchestrator = get_orchestrator()
    orchestrator.execute(objective, collaborate=collaborate, verbose=verbose)

@app.command()
def ingest(path: str):
    """Deep ingest a codebase into G CLI memory."""
    orchestrator = get_orchestrator()
    orchestrator.ingest_codebase(path)

@app.command()
def chat(collaborate: bool = True, verbose: bool = True):
    """Enter the G CLI Cognitive Cockpit."""
    console.print(Panel("[bold cyan]G CLI v2: Cognitive Brain Online[/bold cyan]\nType 'exit' to disconnect."))
    orchestrator = get_orchestrator()
    while True:
        try:
            user_input = typer.prompt(">>")
            if user_input.lower() in ["exit", "quit"]: break
            orchestrator.execute(user_input, collaborate=collaborate, verbose=verbose)
        except KeyboardInterrupt:
            break

@app.command()
def explain(query: str):
    """Explain a complex code pattern or architectural decision."""
    orchestrator = get_orchestrator()
    orchestrator.execute(f"Explain this in depth: {query}")

@app.command()
def debug(issue: str):
    """Solve a complex coding bug using Multi-Model Collaboration."""
    orchestrator = get_orchestrator()
    orchestrator.execute(issue)

if __name__ == "__main__":
    app()

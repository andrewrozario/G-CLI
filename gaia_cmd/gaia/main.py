import os
import sys
import click
from gaia_cmd.core.orchestrator.loop import GaiaOrchestrator
from gaia_cmd.core.ui.cli import GaiaUI
from gaia_cmd.ui.display import GaiaDisplay
from gaia_cmd.core.llm.state import set_model, get_model

# Ensure workspace root is in path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

@click.group(invoke_without_command=True)
@click.argument("task", required=False)
@click.option("--voice", is_flag=True, help="Use voice interaction.")
@click.option("--model", default=None, help="Force LLM provider (e.g. 'local', 'ollama', 'gemini', 'openai').")
@click.pass_context
def cli(ctx, task, voice, model):
    """GAIA CLI: Intelligent Systems Architect Interface."""
    if ctx.invoked_subcommand is None:
        if voice:
            run_voice_command(model=model)
        elif task:
            # Direct execution: gaia "my task"
            run_task(task, model=model)
        else:
            # Full Interactive Terminal Mode
            interactive_loop(model=model)

def run_task(goal: str, model: str = None):
    """One-shot task execution."""
    if model:
        set_model(model)
    
    current_model_name = get_model()
    ui = GaiaUI()
    ui.display.show_header()
    ui.display.show_status_bar(workspace=os.getcwd(), mode="execution", model=current_model_name)
    
    orchestrator = GaiaOrchestrator(workspace_root=os.getcwd(), ui=ui, forced_model=current_model_name)
    orchestrator.run(goal)

def interactive_loop(model: str = None):
    """Continuous AI terminal session."""
    if model:
        set_model(model)
        
    current_model_name = get_model()
    ui = GaiaUI()
    ui.print_welcome()
    
    orchestrator = GaiaOrchestrator(workspace_root=os.getcwd(), ui=ui, forced_model=current_model_name)
    
    while True:
        # Show dynamic status bar with synchronized model
        ui.display.show_status_bar(workspace=os.getcwd(), mode="interactive", model=get_model())
        
        try:
            user_input = ui.ask()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['exit', 'quit', 'bye', 'disconnect']:
                ui.stream_output("Disconnecting from neural substrate. Stay safe.")
                break
            
            # Execute through the orchestrator
            orchestrator.run(user_input)
            
        except KeyboardInterrupt:
            ui.console.print("\n[gaia.gold]✦ Interrupt detected. Returning to core...[/]\n")
            continue
        except Exception as e:
            ui.show_error(f"Logic Substrate Error: {e}")

def run_voice_command(model: str = None):
    if model:
        set_model(model)
    from gaia_cmd.core.voice.manager import VoiceManager
    vm = VoiceManager()
    ui = GaiaUI()
    ui.console.print("[bold blue]🎙  Voice Mode Active. Listening...[/bold blue]")
    command = vm.listen_for_command()
    if command:
        ui.console.print(f"[bold cyan]Recognized:[/bold cyan] {command}")
        vm.speak(f"I heard: {command}. Executing now.")
        run_task(command, model=get_model())
    else:
        ui.show_error("No voice command detected.")

@cli.command()
@click.argument("goal")
@click.option("--model", default=None, help="Force LLM provider.")
def build(goal, model):
    """Build a new project or feature using templates or planning."""
    run_task(f"BUILD: {goal}", model=model)

@cli.command()
@click.argument("issue", required=False)
@click.option("--model", default=None, help="Force LLM provider.")
def debug(issue, model):
    """Diagnose and fix a bug in the current workspace."""
    goal = f"DEBUG: {issue}" if issue else "DEBUG: Scan for errors and fix them."
    run_task(goal, model=model)

@cli.command()
@click.argument("target")
@click.option("--model", default=None, help="Force LLM provider.")
def improve(target, model):
    """Refactor and optimize the specified target code."""
    run_task(f"IMPROVE: {target}", model=model)

@cli.command()
@click.argument("goal")
@click.option("--model", default=None, help="Force LLM provider.")
def plan(goal, model):
    """Generate an execution plan without performing any actions."""
    if model:
        set_model(model)
    current_model_name = get_model()
    ui = GaiaUI()
    ui.display.show_header()
    ui.display.show_status_bar(workspace=os.getcwd(), mode="planning", model=current_model_name)
    ui.stream_output(f"Synthesizing architectural roadmap for: {goal}")
    
    orchestrator = GaiaOrchestrator(workspace_root=os.getcwd(), ui=ui, forced_model=current_model_name)
    orchestrator.run(f"PLAN ONLY: {goal}")

@cli.command()
def upgrade():
    """Trigger a self-upgrade cycle for Gaia CLI."""
    run_task("SYSTEM: Perform a self-upgrade analysis and apply improvements.")

@cli.command()
def listen():
    """Explicitly trigger voice command listening."""
    run_voice_command()

if __name__ == "__main__":
    cli()

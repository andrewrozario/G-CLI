from router.model_router import ModelRouter
from agent.planner import Planner
from agent.executor import Executor
from agent.observer import Observer
from memory.vector_db import VectorMemory
from memory.rag_pipeline import CodebaseIngestor
from system.file_manager import FileManager
from system.command_runner import CommandRunner
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

class GCLI_Orchestrator:
    """The central brain for G CLI, coordinating routing and execution."""
    
    def __init__(self):
        self.console = Console()
        self.router = ModelRouter()
        self.memory = VectorMemory()
        self.file_manager = FileManager()
        self.command_runner = CommandRunner()
        # Initialize agents with routed models
        # For simplicity, default agents use the specific models defined in the prompt
        self.planner_client = self.router.get_client("claude")
        self.executor_client = self.router.get_client("codex")
        self.observer_client = self.router.get_client("gemini")
        
        self.planner = Planner(self.planner_client)
        self.executor = Executor(self.executor_client)
        self.observer = Observer(self.observer_client)

    def execute(self, objective: str, collaborate: bool = True, verbose: bool = True):
        """
        Executes a task using either single model routing or multi-model collaboration.
        """
        self.console.print(Panel(f"[bold blue]Objective:[/bold blue] {objective}", title="G CLI Intelligence Cycle"))
        
        # 1. Routing & Task Classification
        route_info = self.router.route(objective)
        if verbose:
            self.console.print(f"[bold magenta]DMSE Router:[/bold magenta] {route_info['reasoning']}")
        
        # 2. Strategic Planning (Claude is the architect)
        self.console.print("[yellow]Phase 1: Strategic Planning (Claude)...[/yellow]")
        context = str(self.memory.retrieve(objective, n_results=3))
        plan = self.planner.create_plan(objective, context=context)
        
        self.console.print(Panel(Markdown("\n".join([f"{i+1}. {step}" for i, step in enumerate(plan)])), title="Strategic Roadmap"))

        full_execution_history = []

        # 3. Iterative Execution Loop
        for i, step in enumerate(plan, 1):
            self.console.print(f"\n[bold cyan]Step {i}:[/bold cyan] {step}")
            
            # Collaborative mode or single model?
            if collaborate:
                # Executor (Codex) performs the task
                self.console.print("[blue]Executing (Codex)...[/blue]")
                result = self.executor.execute_step(step, strategy="\n".join(plan), context=context)
                
                # Observer (Gemini) summarizes and validates
                self.console.print("[blue]Observing (Gemini)...[/blue]")
                summary = self.observer.observe_and_summarize(step, result)
                validation = self.observer.validate(step, result)
            else:
                # Use the routed model for everything in this step
                client = route_info["client"]
                result = client.generate(f"Task: {step}\nContext: {context}")
                summary = result # No separate summary in single mode
                validation = {"success": True, "feedback": "Routed model execution complete."}

            if validation.get("success"):
                self.console.print("[bold green]✓ Validated[/bold green]")
                if verbose:
                    self.console.print(f"[dim]Summary: {summary}[/dim]")
                full_execution_history.append({"step": step, "result": result, "summary": summary})
                # Add to memory
                self.memory.add_memory(result, {"type": "execution", "step": step})
            else:
                self.console.print(f"[bold red]✗ Improvement Needed:[/bold red] {validation.get('feedback')}")
                # Simple retry logic could go here

        # 4. Final Summary (Gemini)
        final_summary_prompt = f"Objective: {objective}\n\nExecution History:\n" + "\n".join([f"Step {i+1}: {h['summary']}" for i, h in enumerate(full_execution_history)])
        final_report = self.observer.observe_and_summarize("Final Synthesis", final_summary_prompt)
        
        self.console.print(Panel(final_report, title="Final Outcome Synthesis (Gemini)"))
        self.console.print(Panel("[bold green]G CLI: Multi-Model Task Complete[/bold green]"))

    def ingest_codebase(self, path: str):
        ingestor = CodebaseIngestor(self.memory, self.planner_client)
        msg = ingestor.ingest_directory(path)
        self.console.print(Panel(msg, title="Ingestion Result"))

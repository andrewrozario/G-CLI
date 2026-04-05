from agents.architectAgent import ArchitectAgent
from agents.coderAgent import CoderAgent
from agents.researcherAgent import ResearcherAgent
from core.autonomy.goalEngine import GoalEngine
from core.autonomy.taskGenerator import TaskGenerator
from core.autonomy.scheduler import Scheduler
from core.guardrails import Guardrails
from core.revenue.opportunityScanner import OpportunityScanner
from core.revenue.monetizationEngine import MonetizationEngine
from rich.console import Console
from rich.panel import Panel

class CentralOrchestrator:
    """The 'Brain' of G CLI v3. Manages autonomous agents and self-tasking loops."""
    
    def __init__(self):
        self.console = Console()
        # Initialize specialized agents
        self.agents = {
            "architect": ArchitectAgent(),
            "coder": CoderAgent(),
            "researcher": ResearcherAgent()
        }
        
        # Autonomy Core
        self.goals = GoalEngine()
        self.task_generator = TaskGenerator()
        self.scheduler = Scheduler(self)
        
        # Guardrails
        self.guardrails = Guardrails()
        
        # Revenue
        self.scanner = OpportunityScanner()
        self.monetizer = MonetizationEngine()

    def run_autonomy(self, context: str = ""):
        """The main autonomous loop: Scan goals -> Generate Tasks -> Execute."""
        active_goals = self.goals.get_active_goals()
        if not active_goals:
            self.console.print("[yellow]No active goals found. Gaia is in standby.[/yellow]")
            return

        self.console.print(Panel(f"Gaia is thinking autonomously about {len(active_goals)} goals...", title="Gaia v3 Autonomy"))
        
        # 1. Generate Tasks
        tasks = self.task_generator.generate_tasks(active_goals, context)
        
        # 2. Schedule and Execute
        self.scheduler.execute_loop(tasks)

    def process_task(self, task: dict):
        """Dispatches a task to the correct agent based on its nature."""
        name = task.get("name")
        agent_type = task.get("agent_type", "architect") # Default
        description = task.get("description")
        
        self.console.print(f"\n[bold cyan]Agent Dispatch:[/bold cyan] {agent_type} -> {name}")
        
        agent = self.agents.get(agent_type, self.agents["architect"])
        result = agent.act(description)
        
        self.console.print(Panel(result, title=f"{agent.name} Result"))
        return result

    def scan_for_revenue(self, context: str):
        self.console.print("[green]Gaia is scanning for revenue opportunities...[/green]")
        opp = self.scanner.scan(context)
        strategy = self.monetizer.suggest_strategy(opp)
        self.console.print(Panel(strategy, title="Gaia Monetization Strategy"))

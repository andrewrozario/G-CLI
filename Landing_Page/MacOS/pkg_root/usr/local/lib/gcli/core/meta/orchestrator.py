from core.decision.decisionEngine import DecisionEngine
from core.memory.recallEngine import RecallEngine
from core.memory.contextBuilder import ContextBuilder
from core.personality.toneEngine import ToneEngine
from core.personality.userModel import UserModel
from core.gaia.gaiaBridge import GaiaBridge
from router.model_router import ModelRouter
from agent.planner import Planner
from agent.executor import Executor
from agent.observer import Observer
from memory.vector_db import VectorMemory
from system.file_manager import FileManager
from system.command_runner import CommandRunner
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from core.personality.ux_elements import get_random_message, format_result, get_dashboard
from rich.status import Status
from rich.live import Live
from core.autonomy.goalEngine import GoalEngine # Added for dashboard

from core.utils.diff_viewer import show_diff
from core.utils.git_client import GitClient
from core.utils.patcher import Patcher
from core.project.project_scanner import ProjectScanner
from core.project.context_selector import ContextSelector
from core.project.dependency_graph import DependencyGraph
from core.project.impact_analyzer import ImpactAnalyzer
from core.testing.healing_loop import HealingLoop
from memory.long_term_memory import LearningLoop
import typer

class MetaOrchestrator:
    """The master controller evolved for Continuous Self-Improvement."""
    
    def __init__(self):
        self.console = Console()
        self.decision_engine = DecisionEngine()
        self.recall_engine = RecallEngine()
        self.context_builder = ContextBuilder()
        self.tone_engine = ToneEngine()
        self.user_model = UserModel()
        self.gaia_bridge = GaiaBridge()
        self.router = ModelRouter()
        self.vector_memory = VectorMemory()
        self.goal_engine = GoalEngine() # Added
        self.file_manager = FileManager()
        self.command_runner = CommandRunner()
        self.git_client = GitClient()
        self.patcher = Patcher()
        self.project_scanner = ProjectScanner()
        self.context_selector = ContextSelector()
        self.dependency_graph = DependencyGraph()
        self.impact_analyzer = ImpactAnalyzer()
        self.healing_loop = HealingLoop(self)
        self.learning_loop = LearningLoop(self.router.get_client("gemini"))
        self.validate_api_keys()

    def validate_api_keys(self):
        """Verifies that all required brain connections are active."""
        import os
        keys = {
            "ANTHROPIC_API_KEY": "Claude (Architect)",
            "OPENAI_API_KEY": "Codex (Engineer)",
            "GEMINI_API_KEY": "Gemini (Observer)"
        }
        missing = []
        for key, name in keys.items():
            if not os.getenv(key):
                missing.append(name)
        
        if missing:
            self.console.print(f"[bold red][WARNING][/bold red] Missing API connections: {', '.join(missing)}")
            self.console.print("[dim]G CLI will fallback to local intelligence where possible.[/dim]\n")

    def show_workspace_dashboard(self):
        """Displays the expansive startup dashboard."""
        stats = self.gaia_bridge.system.get_snapshot()
        goals = self.goal_engine.get_active_goals()
        context = self.gaia_bridge.device.load_session_state()
        dashboard = get_dashboard(stats, goals, context)
        self.console.print(dashboard)

    def execute(self, objective: str, mode: str = "deep", chain_debug: bool = False, force_model: str = None, force: bool = False, preview: bool = False):
        """
        Executes a task with File-Awareness, Project-Vision, and Direct Action.
        """
        import os
        self.force_execute = force
        self.preview_only = preview
        
        # 0. System-Vision Layer: Directory and File Detection
        detected_files = []
        detected_dirs = []
        words = objective.split()
        for word in words:
            clean_path = word.strip("'\",")
            if os.path.isfile(clean_path):
                detected_files.append(clean_path)
            elif os.path.isdir(clean_path):
                detected_dirs.append(clean_path)

        # Multi-File Intelligence Trigger
        if detected_dirs:
            with Status(f"[bold yellow]G ◦ Scanning project vision...[/bold yellow]", console=self.console) as status:
                all_files = []
                for d in detected_dirs:
                    all_files.extend(self.project_scanner.scan(d))
                
                selected_files = self.context_selector.select(all_files, objective)
                self.console.print(f"🎯 [bold cyan]Surgical Project Analysis:[/bold cyan] Found {len(all_files)} files, selected {len(selected_files)} for modification.")
                
                # Dependency Graph Layer
                status.update("G ◦ Mapping dependency graph...")
                graph = self.dependency_graph.build(all_files)
                
                # Impact Analysis
                impacted = self.impact_analyzer.find_impacted_files(graph, selected_files)
                if impacted:
                    self.console.print(f"\n📌 [bold yellow]Impact Analysis:[/bold yellow]")
                    self.console.print(f"→ Targets: {', '.join([os.path.basename(f) for f in selected_files])}")
                    self.console.print(f"→ Affected Files:")
                    for f in impacted:
                        self.console.print(f"   • {os.path.basename(f)}")
                    self.console.print(f"⚠️  [bold white]This change affects {len(selected_files) + len(impacted)} files.[/bold white]")
                    
                    if not self.force_execute and not typer.confirm("Proceed with systemic changes?"):
                        self.console.print("❌ [bold red]Aborted by user.[/bold red]")
                        return
                    
                    # Add impacted files to the workload
                    selected_files.extend(impacted)

                # Update mode to deep for multi-file operations
                mode = "deep"
                detected_files.extend(selected_files)

        file_context = ""
        for path in set(detected_files): # set() to avoid duplicates
            content = self.file_manager.read_file(path)
            file_context += f"\nFILE: {path}\nCONTENT:\n{content}\n"

        with Status("[bold yellow]G ◦ Analyzing systemic context...[/bold yellow]", console=self.console, spinner="dots") as status:
            try:
                # 1. Recall Memory & Build Context
                status.update(f"G ◦ {get_random_message('THINKING')}")
                recall_data = self.recall_engine.get_context(objective)
                context_injection = self.context_builder.build_prompt_injection(recall_data)
                
                # REINFORCED LEARNING: Inject past successes
                learned_patterns = self.learning_loop.get_relevant_patterns(objective)
                context_injection += f"\n{learned_patterns}"
                
                if file_context:
                    context_injection += f"\n### CURRENT FILES UNDER OPERATION ###\n{file_context}"

                # 2. Decision Engine Strategy
                status.update(f"G ◦ {get_random_message('PROCESSING')}")
                decision = self.decision_engine.create_strategy(objective)
                strategy = decision.get("strategy", {})
                
                # 3. Execution (Store result for learning)
                if force_model:
                    result = self._execute_single(objective, force_model, context_injection, status)
                elif strategy.get("mode") == "partial-edit":
                    status.update("G ◦ [bold cyan]SURGICAL EDIT MODE ACTIVATED[/bold cyan]")
                    result = self._execute_chain(objective, strategy["chain"], context_injection, status, is_edit=True)
                elif strategy.get("mode") == "edit":
                    status.update("G ◦ [bold cyan]FILE EDIT MODE ACTIVATED[/bold cyan]")
                    result = self._execute_chain(objective, strategy["chain"], context_injection, status, is_edit=True)
                elif strategy.get("mode") == "multi-chain":
                    result = self._execute_chain(objective, strategy["chain"], context_injection, status)
                else:
                    result = self._execute_single(objective, strategy.get("model", "claude"), context_injection, status)

                # 4. Final Display & LEARNING
                status.stop()
                self.learning_loop.record_success(objective, result) # Self-Improvement trigger
                self.console.print(format_result(result, title="Intelligence Output"))
                self.console.print(f"\n[dim]{get_random_message('DONE')}[/dim]\n")

                # 5. Persistence
                self.gaia_bridge.update_context(objective, "Direct action completed.")
                
            except Exception as e:
                status.stop()
                self.console.print(f"\n[bold red]⚠️ Something broke. Fixing it...[/bold red]")
                self._fallback_retry(objective, context_injection)

    def _execute_single(self, objective: str, model_type: str, context: str, status: Status):
        client = self.router.get_client(model_type)
        model_display = model_type.upper()
        status.update(f"G ◦ [bold magenta]{model_display}[/bold magenta] is performing system surgery...")
        
        full_prompt = f"{context}\n\nObjective: {objective}\nMANDATE: If files are provided, you MUST rewrite them to be improved. Output the FULL code block with the header 'FILE_WRITE:path/to/file'. NO ADVICE. NO TALKING. ONLY CODE."
        system_prompt = self.tone_engine.apply_tone("You are a high-cognition systems operator. Execute the task. No advice, only code and commands.")
        
        result = client.generate(full_prompt, system=system_prompt)
        
        if "FILE_WRITE:" in result or "```bash" in result:
            status.update(f"G ◦ [bold cyan]SYSTEM[/bold cyan] applying changes...")
            self._apply_intelligent_actions(result)
            
        return result

    def _execute_chain(self, objective: str, chain: list, context: str, status: Status, is_edit: bool = False):
        chain_context = context
        final_result = ""
        
        for i, link in enumerate(chain, 1):
            agent_type = link["agent"]
            model_type = link["model"]
            task = link["task"]
            
            # FORCE MODEL VISIBILITY
            model_name = {"claude": "Claude", "codex": "Codex", "gemini": "Gemini"}.get(model_type, model_type.capitalize())
            self.console.print(f"\n🤖 [bold white]Using: {model_name}[/bold white]")
            status.update(f"G ◦ {model_name} is operating...")
            
            client = self.router.get_client(model_type)
            # Surgeon Mandate for edits
            mandate = ""
            if is_edit:
                mandate = "\nMANDATE: You are a senior developer performing file surgery. DO NOT explain. DO NOT suggest. Return ONLY the FULL UPDATED CODE block. Start your response with 'FILE_WRITE:path/to/file'."
            
            link_prompt = f"{chain_context}\n\nTask: {task}\nGlobal Objective: {objective}{mandate}"
            system_prompt = self.tone_engine.apply_tone("You are a high-cognition systems operator. Execute the task. NO ADVICE. ONLY CODE.")
            
            result = client.generate(link_prompt, system=system_prompt)
            
            # --- THE ACTION LAYER ---
            if "FILE_WRITE:" in result or "```bash" in result:
                status.update(f"G ◦ [bold cyan]SYSTEM[/bold cyan] applying changes to local environment...")
                self._apply_intelligent_actions(result)

            chain_context += f"\n\n--- Output from {model_type} ---\n{result}"
            final_result = result 

        self.vector_memory.add_memory(chain_context, {"type": "chain_execution", "objective": objective})
        return final_result

    def _apply_intelligent_actions(self, output: str):
        """Extracts and executes bash commands or DIRECT file writes with confirmation."""
        import re
        import os
        # 1. Bash Commands
        bash_blocks = re.findall(r"```bash\n(.*?)\n```", output, re.DOTALL)
        for block in bash_blocks:
            for cmd in block.split("\n"):
                if cmd.strip():
                    self.command_runner.run(cmd)

        # 2. Direct File Writes (The Surgeon Protocol with Diff & Confirm)
        write_matches = re.findall(r"FILE_WRITE:(.*?)\n```.*?\n(.*?)\n```", output, re.DOTALL)
        for path, new_content in write_matches:
            path = path.strip()
            
            if os.path.exists(path):
                old_content = self.file_manager.read_file(path)
                show_diff(old_content, new_content)
                
                if self.preview_only:
                    self.console.print(f"👁️ [bold cyan]Preview only mode:[/bold cyan] Changes for {path} displayed but not applied.")
                    continue

                if self.force_execute or typer.confirm(f"💾 [bold cyan]Apply changes to {path}?[/bold cyan]"):
                    # Backup
                    backup_path = path + ".bak"
                    self.file_manager.write_file(backup_path, old_content, backup=False)
                    
                    # Surgical Patch Validation
                    patched_content = self.patcher.validate_and_patch(old_content, new_content)
                    
                    # Write
                    self.file_manager.write_file(path, patched_content, backup=False)
                    self.console.print(f"✅ [bold green]Changes applied.[/bold green]\n🗂  [dim]Backup saved: {backup_path}[/dim]")
                    
                    # SELF-HEALING LAYER
                    healed_content = self.healing_loop.heal(path, patched_content)
                    if healed_content != patched_content:
                        self.console.print("🩹 [bold cyan]Code was autonomously healed to ensure stability.[/bold cyan]")
                    
                    # Git Integration
                    self.git_client.commit(path, f"G CLI: autonomous improvement and verification of {os.path.basename(path)}")
                else:
                    self.console.print(f"❌ [bold red]Changes discarded for {path}.[/bold red]")
            else:
                # New file creation - just confirm creation
                if typer.confirm(f"🆕 [bold cyan]Create new file {path}?[/bold cyan]"):
                    self.file_manager.write_file(path, new_content, backup=False)
                    self.console.print(f"✅ [bold green]File created.[/bold green]")

    def _fallback_retry(self, objective: str, context: str):
        """Emergency fallback using local model if cloud models fail."""
        self.console.print("[yellow]G ◦ Re-routing to core local intelligence...[/yellow]")
        client = self.router.get_client("local")
        result = client.generate(f"Objective: {objective}\nContext: {context}")
        self.console.print(Panel(result, title="⚡ Fallback Result", border_style="yellow"))

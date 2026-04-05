import random

ASCII_ART = r"""
░██████╗    ██████╗██╗     ██╗
██╔════╝   ██╔════╝██║     ██║
██║  ███╗  ██║     ██║     ██║
██║   ██║  ██║     ██║     ██║
╚██████╔╝  ╚██████╗███████╗██║
 ╚═════╝    ╚═════╝╚══════╝╚═╝
"""

SUBTITLES = [
    "You don’t need more answers. You need better questions.",
    "Clarity is the highest form of intelligence.",
    "Speed builds. Depth decides.",
    "Some problems are solved. Others are understood.",
    "The code is the easy part. The logic is the soul.",
    "Elegance is not a luxury, but a necessity."
]

LOADING_MESSAGES = {
    "THINKING": [
        "🧠 Thinking... please don’t rush genius",
        "🧠 Overthinking… but professionally",
        "🧠 Accessing 12% more intelligence than usual",
        "🧠 Simulating 10,000 outcomes..."
    ],
    "PROCESSING": [
        "⚙️ Turning coffee into code…",
        "⚙️ Arguing with itself internally…",
        "⚙️ Summoning brain cells…",
        "⚙️ Realigning neural pathways..."
    ],
    "DEBUGGING": [
        "🐛 Hunting bugs… they’re hiding again",
        "🐛 Fixing things that worked 2 minutes ago",
        "🐛 Negotiating with the compiler..."
    ],
    "HEAVY": [
        "🔥 This one has consequences…",
        "🔥 Thinking harder than your last exam",
        "🔥 Deploying full cognitive focus..."
    ],
    "DONE": [
        "⚡ Done. That was smoother than expected.",
        "⚡ Completed. That felt illegal (in a good way).",
        "⚡ Success. Logic prevails."
    ]
}

from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.console import Group

def get_dashboard(system_stats, goals, context):
    """Creates an expansive, premium dashboard for the boot screen."""
    
    # System Stats Table
    sys_table = Table(title="[bold cyan]System awareness[/bold cyan]", border_style="dim", box=None)
    sys_table.add_column("Resource", style="dim")
    sys_table.add_column("Value", style="bold white")
    sys_table.add_row("CPU Usage", f"{system_stats['cpu_percent']}%")
    sys_table.add_row("RAM Usage", f"{system_stats['ram_percent']}%")
    sys_table.add_row("Disk Space", f"{system_stats['disk_percent']}%")

    # Workspace Table
    ws_table = Table(title="[bold cyan]Workspace Context[/bold cyan]", border_style="dim", box=None)
    ws_table.add_column("Metric", style="dim")
    ws_table.add_column("Status", style="bold white")
    ws_table.add_row("Active Project", context.get("last_objective", "Standby")[:20] + "...")
    ws_table.add_row("Pending Goals", str(len(goals)))
    ws_table.add_row("Cognitive Mode", "Real Intelligence v3")

    return Panel(
        Columns([sys_table, ws_table], expand=True),
        title="[bold white]G CLI COGNITIVE DASHBOARD[/bold white]",
        border_style="cyan",
        padding=(1, 2)
    )

def format_result(content, title="Result"):
    """Expansive, clean result formatting."""
    return Panel(
        content,
        title=f"⚡ [bold green]{title}[/bold green]",
        subtitle="[dim]Gaia Intelligence Output[/dim]",
        border_style="white",
        padding=(1, 2)
    )

def get_random_subtitle():
    return random.choice(SUBTITLES)

def get_random_message(category):
    return random.choice(LOADING_MESSAGES.get(category, LOADING_MESSAGES["THINKING"]))

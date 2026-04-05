import difflib
from rich.console import Console
from rich.text import Text

def show_diff(old_str: str, new_str: str):
    """Displays a professional color-coded diff in the terminal."""
    console = Console()
    console.print("\n🔍 [bold cyan]Changes Preview:[/bold cyan]\n")
    
    diff = difflib.unified_diff(
        old_str.splitlines(keepends=True),
        new_str.splitlines(keepends=True),
        fromfile="Current",
        tofile="Proposed"
    )
    
    for line in diff:
        if line.startswith('+') and not line.startswith('+++'):
            console.print(Text(line, style="green"), end="")
        elif line.startswith('-') and not line.startswith('---'):
            console.print(Text(line, style="red"), end="")
        elif line.startswith(' '):
            console.print(Text(line, style="dim"), end="")
        else:
            console.print(Text(line, style="cyan"), end="")
    console.print("\n")

import os
import shutil
from rich.console import Console

def undo_last_change(file_path: str):
    """Restores a file from its last .bak version."""
    console = Console()
    backup_path = file_path + ".bak"

    if not os.path.exists(backup_path):
        console.print(f"⚠️ [bold red]No backup found for:[/bold red] {file_path}")
        return

    try:
        shutil.copy2(backup_path, file_path)
        console.print(f"↩️ [bold green]Undo successful.[/bold green] Restored {file_path} from backup.")
    except Exception as e:
        console.print(f"❌ [bold red]Failed to restore file:[/bold red] {str(e)}")

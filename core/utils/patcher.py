from rich.console import Console

class Patcher:
    """Ensures surgical precision and validates AI-generated code before patching."""
    def __init__(self):
        self.console = Console()

    def validate_and_patch(self, original: str, updated: str) -> str:
        """Validates that the update is substantial and not a hallucinated explanation."""
        if not updated or len(updated.strip()) < 10:
            self.console.print("⚠️ [bold yellow]Patch validation failed:[/bold yellow] Output too small.")
            return original
        
        if "I cannot" in updated or "As an AI" in updated:
            self.console.print("⚠️ [bold yellow]Patch validation failed:[/bold yellow] AI refused or explained.")
            return original

        # In this elite version, we expect the FULL surgical file from the model.
        return updated

class PermissionSystem:
    """Handles user approval for high-risk or external actions."""
    def request_approval(self, task: dict) -> bool:
        print(f"\n[bold yellow]PERMISSION REQUESTED:[/bold yellow]")
        print(f"Task: {task.get('name', 'Unknown')}")
        print(f"Reason: {task.get('description', 'Autonomous action.')}")
        
        # In a real CLI, we use typer.confirm or rich.prompt
        import typer
        return typer.confirm("Do you approve this action?")

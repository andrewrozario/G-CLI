class Scheduler:
    """Manages the autonomous execution cycle of tasks."""
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator

    def execute_loop(self, tasks: list):
        for task in tasks:
            # Check with Guardrails before each task
            if self.orchestrator.guardrails.approve(task):
                self.orchestrator.process_task(task)
            else:
                print(f"Task blocked by guardrails: {task['name']}")

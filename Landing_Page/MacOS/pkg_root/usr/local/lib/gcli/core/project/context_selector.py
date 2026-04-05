import os

class ContextSelector:
    """Filters scanned files to select only those relevant to the specific task."""
    def __init__(self):
        # Professional-grade extensions
        self.relevant_extensions = {'.py', '.js', '.ts', '.html', '.css', '.md', '.go', '.rs', '.json'}

    def select(self, files: list, task: str) -> list:
        task_lower = task.lower()
        
        # Extension-based filtering
        selected = [f for f in files if os.path.splitext(f)[1] in self.relevant_extensions]
        
        # Keyword-based relevance (Heuristic)
        if "frontend" in task_lower or "ui" in task_lower or "layout" in task_lower:
            selected = [f for f in selected if any(ext in f for ext in ['.html', '.css', '.js', '.ts'])]
        elif "backend" in task_lower or "api" in task_lower:
            selected = [f for f in selected if any(ext in f for ext in ['.py', '.go', '.rs', '.js'])]
            
        # Hard Smart Limit: Max 10 files per surgical run to prevent chaos
        return selected[:10]

class RiskEvaluator:
    """Evaluates the risk and potential cost of an autonomous task."""
    def __init__(self, cost_limit: float = 5.0):
        self.cost_limit = cost_limit

    def evaluate_risk(self, task: dict) -> bool:
        # Simple rule: if cost estimate > limit, return False
        estimated_cost = task.get("estimated_cost", 0.0)
        if estimated_cost > self.cost_limit:
            return False
            
        # Dangerous command detection
        dangerous_cmds = ["rm -rf /", "git push --force", "chmod 777"]
        description = task.get("description", "").lower()
        if any(cmd in description for cmd in dangerous_cmds):
            return False
            
        return True

from .permissionSystem import PermissionSystem
from .riskEvaluator import RiskEvaluator

class Guardrails:
    """The safety gatekeeper for Gaia v3."""
    def __init__(self):
        self.permission = PermissionSystem()
        self.risk = RiskEvaluator()

    def approve(self, task: dict) -> bool:
        # 1. Automatic Risk Assessment
        if not self.risk.evaluate_risk(task):
            print(f"Task failed risk assessment: {task.get('name')}")
            return False
            
        # 2. User Permission (only for medium/high-risk tasks)
        if task.get("risk_level") in ["medium", "high"]:
            return self.permission.request_approval(task)
            
        return True # Low risk, auto-approve

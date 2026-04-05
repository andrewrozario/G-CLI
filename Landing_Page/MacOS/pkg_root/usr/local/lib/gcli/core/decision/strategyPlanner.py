class StrategyPlanner:
    """Builds a technical strategy (single or multi-model) for execution."""
    
    def plan(self, intent: dict, complexity: dict, objective: str) -> dict:
        lower = objective.lower()
        has_path = "/" in objective or "\\" in objective
        
        # SMART MODE DETECTION
        is_refactor = any(kw in lower for kw in ["refactor", "optimize", "clean"])
        is_edit = any(kw in lower for kw in ["improve", "fix", "update", "add"])
        
        # PARTIAL / SURGICAL EDIT MODE
        if is_refactor and has_path:
            return {
                "mode": "partial-edit",
                "chain": [
                    {"agent": "architect", "model": "claude", "task": "analyze minimal surgical improvements"},
                    {"agent": "coder", "model": "codex", "task": "apply precise modifications only and return full file"}
                ]
            }

        # STANDARD FILE EDIT MODE
        if is_edit and has_path:
            return {
                "mode": "edit",
                "chain": [
                    {"agent": "architect", "model": "claude", "task": "analyze and improve this code"},
                    {"agent": "coder", "model": "codex", "task": "apply code improvements and return full updated code"}
                ]
            }

        # DEFAULT CHAT
        return {
            "mode": "chat",
            "model": "gemini" if complexity.get("score", 0) < 5 else "claude"
        }

class ChangeAnalyzer:
    """Analyzes file changes for high-signal issues before triggering AI."""
    
    def analyze(self, file_path: str, content: str) -> list:
        issues = []
        
        # Heuristic checks
        if "console.log" in content or "print(" in content:
            issues.append("Debug logs detected (potential cleanup needed)")
            
        if "TODO" in content or "FIXME" in content:
            issues.append("Pending task markers found")
            
        if "except:" in content and "pass" in content:
            issues.append("Unsafe silent error handling detected")

        return issues

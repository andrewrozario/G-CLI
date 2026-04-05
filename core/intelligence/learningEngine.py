from .routingMemory import RoutingMemory

class LearningEngine:
    """Analyzes past performance to dynamically adjust model routing confidence scores."""
    def __init__(self, memory: RoutingMemory):
        self.memory = memory

    def calculate_confidence(self, model: str, category: str) -> float:
        """
        score = (success_rate * w1) + (speed_factor * w2) - (cost_factor * w3)
        """
        history = self.memory.get_history()
        relevant = [r for r in history if r.get("model") == model and r.get("category") == category]
        
        if not relevant:
            return 50.0  # Base confidence for unknown paths

        total = len(relevant)
        successes = sum(1 for r in relevant if r.get("success", False))
        success_rate = successes / total

        avg_duration = sum(r.get("duration", 1.0) for r in relevant) / total
        speed_factor = 1.0 / (avg_duration + 0.1) # Inverse of duration

        avg_cost = sum(r.get("cost", 0.0) for r in relevant) / total
        
        # Weights
        w1, w2, w3 = 70.0, 20.0, 10.0
        
        score = (success_rate * w1) + (min(speed_factor, 1.0) * w2) - (avg_cost * w3)
        return max(0.0, min(100.0, score)) # Normalize between 0 and 100

    def get_best_model(self, category: str, fallback_model: str) -> str:
        models = ["claude", "codex", "gemini", "local"]
        scores = {m: self.calculate_confidence(m, category) for m in models}
        
        best_model = max(scores, key=scores.get)
        
        # If the best model has a very low confidence, rely on the heuristic fallback
        if scores[best_model] < 30.0:
            return fallback_model
            
        return best_model

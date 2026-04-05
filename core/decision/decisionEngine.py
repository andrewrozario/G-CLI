from .intentAnalyzer import IntentAnalyzer
from .complexityEstimator import ComplexityEstimator
from .strategyPlanner import StrategyPlanner

class DecisionEngine:
    """The G CLI Brain: Analyzes, estimates, and plans before action."""
    def __init__(self):
        self.intent_analyzer = IntentAnalyzer()
        self.complexity_estimator = ComplexityEstimator()
        self.strategy_planner = StrategyPlanner()

    def create_strategy(self, objective: str) -> dict:
        intent = self.intent_analyzer.analyze(objective)
        complexity = self.complexity_estimator.estimate(objective)
        strategy = self.strategy_planner.plan(intent, complexity, objective)
        
        return {
            "objective": objective,
            "intent": intent,
            "complexity": complexity,
            "strategy": strategy
        }

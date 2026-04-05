import time
from .routingMemory import RoutingMemory

class PerformanceTracker:
    """Tracks task metadata including execution time and model selection."""
    def __init__(self, memory: RoutingMemory):
        self.memory = memory
        self._current_task = {}

    def start_tracking(self, objective: str, model_type: str, category: str):
        self._current_task = {
            "objective": objective,
            "model": model_type,
            "category": category,
            "start_time": time.time()
        }

    def end_tracking(self, success: bool, output: str, cost: float = 0.0):
        if not self._current_task:
            return
            
        end_time = time.time()
        duration = end_time - self._current_task["start_time"]
        
        record = {
            "objective": self._current_task["objective"],
            "model": self._current_task["model"],
            "category": self._current_task["category"],
            "duration": duration,
            "success": success,
            "cost": cost,
            "timestamp": time.time()
        }
        self.memory.save_record(record)
        self._current_task = {}

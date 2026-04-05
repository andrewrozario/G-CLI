import logging
from enum import Enum
from typing import Dict, Any, List, Optional

class TaskComplexity(Enum):
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"

class ModelRouter:
    """
    Intelligent routing system for LLM tasks.
    Optimizes performance and cost by selecting the most appropriate model 
    based on task complexity.
    """
    def __init__(self):
        self.logger = logging.getLogger("ModelRouter")
        
        # Keywords that indicate complexity
        self.complexity_indicators = {
            TaskComplexity.COMPLEX: [
                "architect", "design system", "multi-module", "restructure", 
                "refactor entire", "security audit", "optimize performance",
                "scalability", "concurrency", "distributed"
            ],
            TaskComplexity.MEDIUM: [
                "refactor", "implement", "add feature", "fix bug", "test", 
                "validate", "logic", "algorithm", "class", "module"
            ],
            TaskComplexity.SIMPLE: [
                "read", "list", "status", "print", "echo", "check", 
                "create file", "delete", "rename", "move"
            ]
        }

    def evaluate_complexity(self, task_description: str) -> TaskComplexity:
        """
        Analyzes the task description to determine its complexity level.
        """
        task_lower = task_description.lower()
        
        # Check for complex indicators first
        for indicator in self.complexity_indicators[TaskComplexity.COMPLEX]:
            if indicator in task_lower:
                return TaskComplexity.COMPLEX
                
        # Check for medium indicators
        for indicator in self.complexity_indicators[TaskComplexity.MEDIUM]:
            if indicator in task_lower:
                return TaskComplexity.MEDIUM
                
        # Default to simple if many small keywords or short description
        if len(task_description.split()) < 10:
            return TaskComplexity.SIMPLE
            
        return TaskComplexity.SIMPLE

    def get_route(self, task_description: str) -> Dict[str, Any]:
        """
        Returns the recommended model route.
        """
        complexity = self.evaluate_complexity(task_description)
        
        if complexity == TaskComplexity.COMPLEX:
            return {
                "primary": "gemini",
                "fallback": ["ollama", "openai"],
                "refinement_required": True,
                "complexity": complexity.value
            }
        elif complexity == TaskComplexity.MEDIUM:
            return {
                "primary": "ollama",
                "fallback": ["gemini", "openai"],
                "refinement_required": True,
                "complexity": complexity.value
            }
        else:
            return {
                "primary": "ollama",
                "fallback": ["gemini"],
                "refinement_required": False,
                "complexity": complexity.value
            }

from enum import Enum
from typing import List, Dict, Any, Optional
import uuid

class StepStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class SystemDesign:
    """
    Represents the high-level architecture and strategic decisions before implementation.
    """
    def __init__(self, 
                 architecture_type: str, 
                 tech_stack: Dict[str, str], 
                 components: List[Dict[str, Any]], 
                 risks: List[Dict[str, str]], 
                 reasoning: str):
        self.architecture_type = architecture_type
        self.tech_stack = tech_stack
        self.components = components
        self.risks = risks
        self.reasoning = reasoning

    def to_dict(self) -> Dict[str, Any]:
        return {
            "architecture_type": self.architecture_type,
            "tech_stack": self.tech_stack,
            "components": self.components,
            "risks": self.risks,
            "reasoning": self.reasoning
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SystemDesign':
        if not data:
            return None
        return cls(
            architecture_type=data.get("architecture_type", "modular"),
            tech_stack=data.get("tech_stack", {}),
            components=data.get("components", []),
            risks=data.get("risks", []),
            reasoning=data.get("reasoning", "")
        )

class TaskStep:
    """
    A single granular unit of work within an ExecutionPlan.
    """
    def __init__(self, 
                 description: str, 
                 goal: str, 
                 dependencies: List[str] = None, 
                 required_files: List[str] = None, 
                 required_tools: List[str] = None,
                 id: str = None):
        self.id = id or str(uuid.uuid4())[:8]
        self.description = description
        self.goal = goal
        self.dependencies = dependencies or []
        self.required_files = required_files or []
        self.required_tools = required_tools or []
        self.status = StepStatus.PENDING
        self.result: Optional[Dict[str, Any]] = None
        self.attempts = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "goal": self.goal,
            "dependencies": self.dependencies,
            "required_files": self.required_files,
            "required_tools": self.required_tools,
            "status": self.status.value,
            "attempts": self.attempts
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskStep':
        step = cls(
            description=data["description"],
            goal=data["goal"],
            dependencies=data.get("dependencies", []),
            required_files=data.get("required_files", []),
            required_tools=data.get("required_tools", []),
            id=data.get("id")
        )
        step.status = StepStatus(data.get("status", "pending"))
        step.attempts = data.get("attempts", 0)
        return step

class ExecutionPlan:
    """
    A Directed Acyclic Graph (DAG) of TaskSteps representing the full strategy.
    Now includes a SystemDesign for strategic implementation.
    """
    def __init__(self, goal: str, design: Optional[SystemDesign] = None):
        self.goal = goal
        self.design = design
        self.steps: Dict[str, TaskStep] = {}
        self.created_at = None

    def add_step(self, step: TaskStep):
        self.steps[step.id] = step

    def get_next_runnable_steps(self) -> List[TaskStep]:
        runnable = []
        for step in self.steps.values():
            if step.status == StepStatus.PENDING:
                all_deps_done = True
                for dep_id in step.dependencies:
                    dep = self.steps.get(dep_id)
                    if not dep or dep.status != StepStatus.COMPLETED:
                        all_deps_done = False
                        break
                if all_deps_done:
                    runnable.append(step)
        return runnable

    def is_complete(self) -> bool:
        return all(s.status == StepStatus.COMPLETED or s.status == StepStatus.SKIPPED for s in self.steps.values())

    def has_failures(self) -> bool:
        return any(s.status == StepStatus.FAILED for s in self.steps.values())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "goal": self.goal,
            "design": self.design.to_dict() if self.design else None,
            "steps": [s.to_dict() for s in self.steps.values()]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExecutionPlan':
        design_data = data.get("design")
        design = SystemDesign.from_dict(design_data) if design_data else None
        plan = cls(goal=data.get("goal", ""), design=design)
        for step_data in data.get("steps", []):
            step = TaskStep.from_dict(step_data)
            plan.add_step(step)
        return plan

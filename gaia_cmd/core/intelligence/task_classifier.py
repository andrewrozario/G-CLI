import json
import logging
from enum import Enum
from typing import Dict, Any, Optional
from gaia_cmd.core.llm.provider import LLMProvider
from gaia_cmd.core.llm.safe_generate import safe_generate

class TaskType(Enum):
    FILE_OPERATION = "FILE_OPERATION"
    CODE_GENERATION = "CODE_GENERATION"
    SYSTEM_COMMAND = "SYSTEM_COMMAND"
    ANALYSIS = "ANALYSIS"
    MULTI_STEP = "MULTI_STEP"

class TaskClassifier:
    """
    Intelligence layer that classifies incoming user requests into specific task types.
    Ensures the orchestrator selects the optimal execution path.
    """
    def __init__(self, llm: LLMProvider):
        self.llm = llm
        self.logger = logging.getLogger("TaskClassifier")

    def classify_task(self, prompt: str) -> Dict[str, Any]:
        """
        Analyzes the prompt to determine task type and confidence.
        Uses LLM with keyword-based auto-inference as a fallback.
        """
        self.logger.info(f"Classifying task: {prompt[:50]}...")

        system_prompt = (
            "You are the Gaia CLI Task Classifier. Your job is to categorize user requests into exactly one of the following types:\n"
            "1. FILE_OPERATION: Creating, moving, deleting, or reading files without significant logic generation.\n"
            "2. CODE_GENERATION: Writing algorithms, building features, refactoring code, or implementing logic.\n"
            "3. SYSTEM_COMMAND: Running terminal commands, installing packages, or environment setup.\n"
            "4. ANALYSIS: Auditing code, searching for patterns, explaining logic, or architecture review.\n"
            "5. MULTI_STEP: Complex requests that involve multiple of the above categories or require a deep plan.\n\n"
            "Respond ONLY with a valid JSON object: {'type': 'TYPE_NAME', 'confidence': 0.XX, 'reasoning': '...'}"
        )

        result = {
            "type": TaskType.MULTI_STEP.value,
            "confidence": 0.0,
            "reasoning": "Default fallback"
        }

        try:
            response_data = safe_generate(self.llm, [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"CLASSIFY THIS TASK: {prompt}"}
            ], task_description=f"Classifying: {prompt[:30]}")
            
            content = response_data.get("content", "").strip()
            
            # Clean JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "{" in content:
                content = content[content.find("{"):content.rfind("}")+1]
            
            llm_result = json.loads(content)
            
            # Validate type against Enum
            try:
                llm_result["type"] = TaskType(llm_result["type"]).value
                result = llm_result
            except ValueError:
                self.logger.warning(f"Invalid task type returned: {llm_result['type']}. Using inference.")
                result["confidence"] = 0.0

        except Exception as e:
            self.logger.error(f"Task classification LLM call failed: {e}")
            result["confidence"] = 0.0

        # Auto-Inference Fallback for low confidence
        if result["confidence"] < 0.7:
            inferred_type = self._infer_task_type(prompt)
            if inferred_type:
                result["type"] = inferred_type.value
                result["confidence"] = 0.8 # Boost confidence for successful keyword match
                result["reasoning"] = f"Inferred from keywords in prompt."
            else:
                result["type"] = TaskType.MULTI_STEP.value
                result["confidence"] = 0.5
                result["reasoning"] = "Uncertain intent, defaulting to MULTI_STEP."

        return result

    def _infer_task_type(self, prompt: str) -> Optional[TaskType]:
        """
        Heuristic-based task inference using keywords.
        """
        p = prompt.lower()
        
        # 1. FILE_OPERATION
        if any(kw in p for kw in ["clone", "copy", "directory", "folder", "move", "rename", "delete"]):
            return TaskType.FILE_OPERATION
            
        # 2. CODE_GENERATION
        if any(kw in p for kw in ["build", "code", "write", "implement", "refactor", "algorithm"]):
            return TaskType.CODE_GENERATION
            
        # 3. SYSTEM_COMMAND
        if any(kw in p for kw in ["install", "run", "npm", "pip", "execute", "setup", "command"]):
            return TaskType.SYSTEM_COMMAND
            
        return None

import json
import logging
import os
import time
import threading
from typing import Any, Dict, List, Optional
import uuid

class PersistentMemory:
    """
    Simulates infinite context using structured JSON persistence.
    Manages historical tasks, successful solutions, architectural patterns, and experiences.
    """
    def __init__(self, memory_root: str):
        self.logger = logging.getLogger("PersistentMemory")
        self.memory_root = memory_root
        self._lock = threading.Lock()
        
        self.files = {
            "tasks": os.path.join(memory_root, "tasks.json"),
            "solutions": os.path.join(memory_root, "solutions.json"),
            "patterns": os.path.join(memory_root, "patterns.json"),
            "experience": os.path.join(memory_root, "experience.json")
        }
        
        self._ensure_storage()
        self.cache: Dict[str, List[Dict[str, Any]]] = self._load_all()

    def _ensure_storage(self):
        os.makedirs(self.memory_root, exist_ok=True)
        for path in self.files.values():
            if not os.path.exists(path):
                with open(path, 'w') as f:
                    json.dump([], f)

    def _load_all(self) -> Dict[str, List[Dict[str, Any]]]:
        data = {}
        for key, path in self.files.items():
            try:
                with open(path, 'r') as f:
                    data[key] = json.load(f)
            except Exception as e:
                self.logger.error(f"Failed to load {key} memory: {e}")
                data[key] = []
        return data

    def _save(self, key: str):
        try:
            with open(self.files[key], 'w') as f:
                json.dump(self.cache[key], f, indent=4)
        except Exception as e:
            self.logger.error(f"Failed to save {key} memory: {e}")

    def save_task(self, task: str, output: str, success: bool, metadata: Optional[Dict[str, Any]] = None):
        """Persists a task and its outcome."""
        with self._lock:
            entry = {
                "id": str(uuid.uuid4()),
                "task": task,
                "output": output,
                "success": success,
                "timestamp": time.time(),
                "metadata": metadata or {}
            }
            self.cache["tasks"].append(entry)
            self._save("tasks")
            
            if success:
                # Also promote to solutions if successful
                self._add_solution(task, output, entry["id"])

    def _add_solution(self, task: str, output: str, task_id: str):
        """Internal: Adds a successful task to the solutions pool."""
        solution = {
            "id": str(uuid.uuid4()),
            "task_id": task_id,
            "task": task,
            "solution": output,
            "relevance": 1.0,
            "timestamp": time.time()
        }
        self.cache["solutions"].append(solution)
        self._save("solutions")

    def save_pattern(self, name: str, description: str, usage_context: str):
        """Persists an architectural pattern."""
        with self._lock:
            pattern = {
                "id": str(uuid.uuid4()),
                "name": name,
                "description": description,
                "context": usage_context,
                "timestamp": time.time()
            }
            self.cache["patterns"].append(pattern)
            self._save("patterns")

    def save_experience(self, problem: str, solution: str, errors: List[str], fixes: List[str]):
        """
        Saves a refined experience entry for learning.
        """
        with self._lock:
            experience = {
                "id": str(uuid.uuid4()),
                "problem": problem,
                "solution": solution,
                "errors": errors,
                "fixes": fixes,
                "timestamp": time.time()
            }
            self.cache["experience"].append(experience)
            self._save("experience")
            self.logger.info(f"Experience learned: {problem[:50]}...")

    def retrieve_similar(self, query: str, category: str = "tasks", limit: int = 3) -> List[Dict[str, Any]]:
        """Retrieves and ranks relevant past entries using keyword relevance."""
        with self._lock:
            if category not in self.cache:
                return []
                
            query_words = set(query.lower().split())
            results = []
            
            for entry in self.cache[category]:
                # Combine searchable text based on category
                text = ""
                if category == "tasks":
                    text = entry["task"].lower()
                elif category == "solutions":
                    text = entry["task"].lower() + " " + entry["solution"].lower()
                elif category == "patterns":
                    text = entry["name"].lower() + " " + entry["description"].lower()
                elif category == "experience":
                    text = entry["problem"].lower() + " " + " ".join(entry["errors"]).lower()
                
                # Rank relevance
                match_count = sum(1 for word in query_words if word in text)
                if match_count > 0:
                    # Score = matches * base relevance (if exists)
                    score = match_count * entry.get("relevance", 1.0)
                    results.append((score, entry))
            
            # Sort by score descending
            results.sort(key=lambda x: x[0], reverse=True)
            return [r[1] for r in results[:limit]]

    def get_infinite_context(self, current_task: str) -> str:
        """Formulates context block from all persistent stores."""
        tasks = self.retrieve_similar(current_task, "tasks", limit=2)
        solutions = self.retrieve_similar(current_task, "solutions", limit=2)
        patterns = self.retrieve_similar(current_task, "patterns", limit=2)
        experiences = self.retrieve_similar(current_task, "experience", limit=2)
        
        context = []
        
        if experiences:
            context.append("### NEURAL EXPERIENCE (Problem -> Fix) ###")
            for e in experiences:
                context.append(f"- Problem: {e['problem']}")
                if e['errors']:
                    context.append(f"  Encountered: {', '.join(e['errors'])}")
                if e['fixes']:
                    context.append(f"  Fix: {', '.join(e['fixes'])}")
                context.append(f"  Outcome: {e['solution'][:200]}...")

        if tasks:
            context.append("\n### RELEVANT PAST TASKS ###")
            for t in tasks:
                status = "SUCCESS" if t['success'] else "FAILED"
                context.append(f"- [{status}] {t['task']}")
                
        if solutions:
            context.append("\n### PROVEN SOLUTIONS ###")
            for s in solutions:
                context.append(f"- Task: {s['task']}\n  Logic: {s['solution'][:200]}...")
                
        if patterns:
            context.append("\n### RELEVANT ARCHITECTURAL PATTERNS ###")
            for p in patterns:
                context.append(f"- {p['name']}: {p['description']}")
                
        return "\n".join(context) if context else "No historical precedents found."

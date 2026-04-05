import json
import logging
import os
import threading
from typing import Any, Dict, List, Optional

class LongTermMemory:
    """
    Persistent memory store for project architecture, coding preferences,
    and reusable patterns. Thread-safe implementation.
    """
    def __init__(self, workspace_root: str):
        self.logger = logging.getLogger("LongTermMemory")
        self.workspace_root = workspace_root
        self._lock = threading.Lock()
        
        self.storage_file = os.path.join(workspace_root, "memory", "data", "long_term.json")
        self._ensure_storage()
        self.data = self._load()

    def _ensure_storage(self):
        with self._lock:
            os.makedirs(os.path.dirname(self.storage_file), exist_ok=True)
            if not os.path.exists(self.storage_file):
                with open(self.storage_file, 'w') as f:
                    json.dump({
                        "preferences": [],
                        "patterns": [],
                        "architecture": [],
                        "facts": []
                    }, f)

    def _load(self) -> Dict[str, List[str]]:
        try:
            with open(self.storage_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load long-term memory: {e}")
            return {"preferences": [], "patterns": [], "architecture": [], "facts": []}

    def _save(self):
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            self.logger.error(f"Failed to save long-term memory: {e}")

    def add_insight(self, category: str, insight: str):
        with self._lock:
            if category not in self.data:
                self.data[category] = []
            
            if insight not in self.data[category]:
                self.data[category].append(insight)
                self._save()
                self.logger.info(f"Learned new {category}: {insight}")

    def search(self, query: str, limit: int = 3) -> List[str]:
        with self._lock:
            self.logger.debug(f"Searching long-term memory for: {query}")
            results = []
            query_words = query.lower().split()
            
            for category, items in self.data.items():
                for item in items:
                    score = sum(1 for word in query_words if word in item.lower())
                    if score > 0:
                        results.append((score, f"[{category.upper()}] {item}"))
                        
            results.sort(key=lambda x: x[0], reverse=True)
            return [r[1] for r in results[:limit]]

    def get_all_context(self) -> str:
        with self._lock:
            lines = []
            for category, items in self.data.items():
                if items:
                    lines.append(f"--- {category.capitalize()} ---")
                    lines.extend([f"- {item}" for item in items])
            return "\n".join(lines)

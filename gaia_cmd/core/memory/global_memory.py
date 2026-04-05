import json
import logging
import os
import time
import threading
from typing import Any, Dict, List, Optional
import uuid

class GlobalMemory:
    """
    Persistent, cross-project memory store for Gaia CLI.
    Thread-safe implementation for parallel agent execution.
    """
    def __init__(self, global_root: Optional[str] = None):
        self.logger = logging.getLogger("GlobalMemory")
        self._lock = threading.Lock()
        
        if not global_root:
            home = os.path.expanduser("~")
            global_root = os.path.join(home, ".gaia", "memory")
            
        self.storage_path = global_root
        self.data_file = os.path.join(self.storage_path, "global_memory.json")
        self._ensure_storage()
        self.data = self._load()

    def _ensure_storage(self):
        with self._lock:
            os.makedirs(self.storage_path, exist_ok=True)
            if not os.path.exists(self.data_file):
                with open(self.data_file, 'w') as f:
                    json.dump({
                        "entries": [],
                        "index": {} 
                    }, f)

    def _load(self) -> Dict[str, Any]:
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load global memory: {e}")
            return {"entries": [], "index": {}}

    def _save(self):
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            self.logger.error(f"Failed to save global memory: {e}")

    def add_entry(self, content: str, category: str, tags: List[str] = None, success: bool = True, project: str = "unknown", metadata: Dict[str, Any] = None):
        with self._lock:
            entry = {
                "id": str(uuid.uuid4()),
                "content": content,
                "category": category, 
                "tags": tags or [],
                "success": success,
                "project": project,
                "timestamp": time.time(),
                "relevance_score": 1.0, 
                "metadata": metadata or {}
            }
            
            self.data["entries"].append(entry)
            self._save()
            self.logger.info(f"Global memory learned new {category} from project '{project}'")

    def search(self, query: str, limit: int = 5, category: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._lock:
            query_words = set(query.lower().split())
            results = []
            
            for entry in self.data["entries"]:
                if category and entry["category"] != category:
                    continue
                    
                content_lower = entry["content"].lower()
                tags_lower = [t.lower() for t in entry["tags"]]
                
                word_score = sum(1 for word in query_words if word in content_lower)
                tag_score = sum(2 for word in query_words if word in tags_lower)
                
                final_score = (word_score + tag_score) * entry.get("relevance_score", 1.0)
                
                if final_score > 0:
                    results.append((final_score, entry))
                    
            results.sort(key=lambda x: x[0], reverse=True)
            return [r[1] for r in results[:limit]]

    def record_success(self, entry_id: str):
        with self._lock:
            for entry in self.data["entries"]:
                if entry["id"] == entry_id:
                    entry["relevance_score"] += 0.1
                    self._save()
                    break

    def get_context_for_prompt(self, query: str, limit: int = 5) -> str:
        entries = self.search(query, limit=limit)
        if not entries:
            return "No relevant cross-project knowledge found."
            
        formatted_entries = []
        for e in entries:
            prefix = f"[{e['category'].upper()}]"
            if not e.get("success", True):
                prefix = f"[PAST MISTAKE - AVOID]"
            
            tags = f" (Tags: {', '.join(e['tags'])})" if e['tags'] else ""
            formatted_entries.append(f"{prefix} {e['content']}{tags}")
            
        return "\n".join(formatted_entries)

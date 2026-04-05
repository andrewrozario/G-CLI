import os
import json

class VectorMemory:
    """Mock Vector Memory using local JSON storage to bypass chromadb dependency issues."""
    def __init__(self, db_path: str = "./.gaia_memory"):
        self.db_path = db_path
        os.makedirs(db_path, exist_ok=True)
        self.storage_file = os.path.join(db_path, "mock_memory.json")
        self.data = self._load_data()

    def _load_goals(self) -> list:
        if os.path.exists(self.storage_file):
            with open(self.storage_file, 'r') as f:
                return json.load(f)
        return []

    def _load_data(self) -> dict:
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_data(self):
        with open(self.storage_file, 'w') as f:
            json.dump(self.data, f, indent=2)

    def add_memory(self, text: str, metadata: dict, doc_id: str = None, collection_name: str = "knowledge"):
        if collection_name not in self.data:
            self.data[collection_name] = []
        
        self.data[collection_name].append({
            "text": text,
            "metadata": metadata,
            "id": doc_id or str(len(self.data[collection_name]))
        })
        self._save_data()

    def retrieve(self, query: str, n_results: int = 3, collection_name: str = "knowledge") -> list:
        collection = self.data.get(collection_name, [])
        # Simple mock retrieval (last N items)
        results = [item["text"] for item in collection[-n_results:]]
        return results

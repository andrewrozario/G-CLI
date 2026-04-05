import re
import os
import networkx as nx
import json
from typing import Dict, List, Any

class StructuralAnalyzer:
    """Advanced AST-like parser and Knowledge Graph for codebases."""
    
    PATTERNS = {
        "python": {
            "function": r"def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(",
            "class": r"class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[:\(]",
            "import": r"import\s+([a-zA-Z0-9_\.]+)|from\s+([a-zA-Z0-9_\.]+)\s+import",
            "call": r"([a-zA-Z_][a-zA-Z0-9_]*)\("
        },
        "javascript": {
            "function": r"function\s+([a-zA-Z_][a-zA-Z0-9_]*)|const\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*\(",
            "class": r"class\s+([a-zA-Z_][a-zA-Z0-9_]*)",
            "import": r"import\s+.*\s+from\s+['\"](.*)['\"]|require\(['\"](.*)['\"]\)",
            "call": r"([a-zA-Z_][a-zA-Z0-9_]*)\("
        }
    }

    def __init__(self, storage_path: str = "./.gaia_memory/knowledge_graph.json"):
        self.storage_path = storage_path
        self.graph = nx.DiGraph()
        if os.path.exists(storage_path):
            self.load_graph()

    def analyze_file(self, file_path: str, content: str) -> Dict[str, Any]:
        ext = os.path.splitext(file_path)[1].lstrip('.')
        lang = "python" if ext == "py" else "javascript" if ext in ["js", "ts"] else "generic"
        
        patterns = self.PATTERNS.get(lang, self.PATTERNS["python"]) # Fallback
        
        symbols = {
            "functions": list(set(re.findall(patterns["function"], content))),
            "classes": list(set(re.findall(patterns["class"], content))),
            "imports": [match[0] or match[1] for match in re.findall(patterns["import"], content) if any(match)],
            "calls": list(set(re.findall(patterns["call"], content)))
        }
        
        # Node creation with metadata
        self.graph.add_node(file_path, type="file", lang=lang, **symbols)
        
        # Edge creation for imports (dependencies)
        for imp in symbols["imports"]:
            self.graph.add_edge(file_path, imp, relation="imports")
            
        # Edge creation for calls (potential coupling)
        for call in symbols["calls"]:
            if call not in ["print", "len", "dict", "list", "set", "range"]: # Ignore built-ins
                self.graph.add_node(call, type="function_call")
                self.graph.add_edge(file_path, call, relation="calls")
            
        return symbols

    def save_graph(self):
        data = nx.node_link_data(self.graph)
        with open(self.storage_path, 'w') as f:
            json.dump(data, f)

    def load_graph(self):
        with open(self.storage_path, 'r') as f:
            data = json.load(f)
            self.graph = nx.node_link_graph(data)

    def get_neighbors(self, node: str) -> List[str]:
        if node in self.graph:
            return list(self.graph.neighbors(node))
        return []

    def find_path(self, start_node: str, end_node: str):
        try:
            return nx.shortest_path(self.graph, start_node, end_node)
        except:
            return None

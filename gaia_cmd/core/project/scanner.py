import os
import json
import logging
from typing import Dict, Any, List, Optional

class ProjectScanner:
    """
    Scans the project directory to identify technologies, 
    dependencies, entry points, and architectural patterns.
    """
    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root
        self.logger = logging.getLogger("ProjectScanner")
        self.ignored_dirs = {".git", "node_modules", "__pycache__", "venv", ".venv", "dist", "build"}

    def scan(self) -> Dict[str, Any]:
        """
        Performs a full scan of the project and returns a structured map.
        """
        self.logger.info(f"Scanning project at: {self.workspace_root}")
        
        project_data = {
            "root": self.workspace_root,
            "technologies": self._detect_technologies(),
            "dependencies": self._parse_dependencies(),
            "structure": self._get_structure(self.workspace_root),
            "entry_points": self._find_entry_points(),
            "patterns": self._identify_patterns()
        }
        
        return project_data

    def _detect_technologies(self) -> List[str]:
        """Identifies languages and frameworks used."""
        tech = set()
        for root, dirs, files in os.walk(self.workspace_root):
            dirs[:] = [d for d in dirs if d not in self.ignored_dirs]
            for f in files:
                if f.endswith(".py"): tech.add("Python")
                if f.endswith(".js") or f.endswith(".jsx"): tech.add("JavaScript/React")
                if f.endswith(".ts") or f.endswith(".tsx"): tech.add("TypeScript/React")
                if f.endswith(".go"): tech.add("Go")
                if f.endswith(".rs"): tech.add("Rust")
                if f == "package.json": tech.add("Node.js")
                if f == "requirements.txt" or f == "pyproject.toml": tech.add("Python")
                if f == "Docker_file" or f == "docker-compose.yml": tech.add("Docker")
        return list(tech)

    def _parse_dependencies(self) -> Dict[str, List[str]]:
        """Extracts key dependencies from config files."""
        deps = {"npm": [], "pip": []}
        
        # Parse package.json
        pkg_path = os.path.join(self.workspace_root, "package.json")
        if os.path.exists(pkg_path):
            try:
                with open(pkg_path, "r") as f:
                    data = json.load(f)
                    deps["npm"] = list(data.get("dependencies", {}).keys())
            except: pass

        # Parse requirements.txt
        req_path = os.path.join(self.workspace_root, "requirements.txt")
        if os.path.exists(req_path):
            try:
                with open(req_path, "r") as f:
                    deps["pip"] = [line.split("==")[0].strip() for line in f if line.strip() and not line.startswith("#")]
            except: pass
            
        return deps

    def _get_structure(self, path: str, depth: int = 0) -> Dict[str, Any]:
        """Recursively builds a tree of the folder structure."""
        if depth > 3: return {"type": "dir", "truncated": True} # Prevent infinite recursion or massive maps
        
        name = os.path.basename(path)
        if os.path.isdir(path):
            items = {}
            try:
                for entry in os.listdir(path):
                    if entry in self.ignored_dirs: continue
                    full_path = os.path.join(path, entry)
                    items[entry] = self._get_structure(full_path, depth + 1)
                return {"type": "directory", "children": items}
            except:
                return {"type": "directory", "error": "Could not read"}
        else:
            return {"type": "file", "size": os.path.getsize(path)}

    def _find_entry_points(self) -> List[str]:
        """Looks for common entry points like main.py, index.js, app.py, etc."""
        entries = []
        common_names = ["main.py", "app.py", "index.js", "index.ts", "server.js", "manage.py"]
        for root, dirs, files in os.walk(self.workspace_root):
            dirs[:] = [d for d in dirs if d not in self.ignored_dirs]
            for f in files:
                if f in common_names:
                    entries.append(os.path.relpath(os.path.join(root, f), self.workspace_root))
        return entries

    def _identify_patterns(self) -> List[str]:
        """Heuristic-based architectural pattern identification."""
        patterns = []
        dir_names = [d for d in os.listdir(self.workspace_root) if os.path.isdir(os.path.join(self.workspace_root, d))]
        
        if "src" in dir_names: patterns.append("Standard Source Layout")
        if "core" in dir_names and "agents" in dir_names: patterns.append("Agentic Architecture (Gaia-style)")
        if "controllers" in dir_names and "models" in dir_names: patterns.append("MVC Pattern")
        if "components" in dir_names and "pages" in dir_names: patterns.append("Component-based (React/Next.js)")
        
        return patterns

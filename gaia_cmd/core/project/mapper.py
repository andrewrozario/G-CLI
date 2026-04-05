import json
import os
import logging
from typing import Dict, Any, List, Optional
from gaia_cmd.core.project.scanner import ProjectScanner

class ProjectMapper:
    """
    Manages the persistent 'project_map.json' and handles high-level queries
    about the project architecture.
    """
    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root
        self.logger = logging.getLogger("ProjectMapper")
        self.map_file = os.path.join(workspace_root, "memory", "project", "project_map.json")
        self.scanner = ProjectScanner(workspace_root)
        self._ensure_map()
        self.project_data = self._load_map()

    def _ensure_map(self):
        """Creates the map if it doesn't exist."""
        os.makedirs(os.path.dirname(self.map_file), exist_ok=True)
        if not os.path.exists(self.map_file):
            self.refresh_map()

    def refresh_map(self):
        """Runs the scanner and updates the project_map.json."""
        self.logger.info("Refreshing project map...")
        self.project_data = self.scanner.scan()
        with open(self.map_file, "w") as f:
            json.dump(self.project_data, f, indent=4)
        self.logger.info("Project map updated.")

    def _load_map(self) -> Dict[str, Any]:
        """Loads the project map from disk."""
        try:
            with open(self.map_file, "r") as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load project map: {e}")
            return {}

    def get_summary_for_prompt(self) -> str:
        """Returns a summarized project overview for injection into AI prompts."""
        d = self.project_data
        summary = f"""
### PROJECT INTELLIGENCE ###
Technologies: {', '.join(d.get('technologies', []))}
Patterns: {', '.join(d.get('patterns', []))}
Entry Points: {', '.join(d.get('entry_points', []))}
Key Dependencies: {', '.join(d.get('dependencies', {}).get('npm', [])[:5])} ...
"""
        return summary

    def query_project(self, query: str) -> str:
        """
        Simple keyword-based retrieval of project components.
        In a real scenario, this would be an LLM-based architectural summary.
        """
        query_lower = query.lower()
        if "auth" in query_lower:
            return "Searching for authentication... Found 'auth' keyword in logic. Probable auth entry point in 'core/auth' or similar."
        if "dependencies" in query_lower:
            return f"Project depends on: {self.project_data.get('dependencies', {})}"
        
        return "Query results: No specific direct mapping found in static project map. Suggesting deep scan."

    def suggest_improvements(self) -> List[str]:
        """Analyzes the project map to suggest architectural improvements."""
        suggestions = []
        d = self.project_data
        
        if len(d.get('entry_points', [])) > 3:
            suggestions.append("Found multiple entry points. Consider consolidating into a single main entry to reduce cognitive load.")
        
        if "Standard Source Layout" not in d.get('patterns', []):
            suggestions.append("Project lacks a standard 'src/' folder. Moving source code to a dedicated folder improves maintainability.")
            
        if not d.get('technologies'):
            suggestions.append("Project type not clearly identified. Adding a README.md or package.json/requirements.txt is recommended.")
            
        return suggestions

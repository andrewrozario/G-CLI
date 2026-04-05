import os
import json
import logging
from typing import Dict, List, Optional, Any
from gaia_cmd.core.llm.manager import LLMManager

class TemplateManager:
    """
    Manages the loading, matching, and customization of project templates.
    """
    def __init__(self, templates_root: str, llm_manager: Optional[LLMManager] = None):
        self.templates_root = templates_root
        self.llm_manager = llm_manager
        self.logger = logging.getLogger("TemplateManager")
        self.templates = self._load_all_metadata()

    def _load_all_metadata(self) -> Dict[str, Any]:
        """Loads metadata for all templates in the templates_root."""
        templates = {}
        if not os.path.exists(self.templates_root):
            self.logger.warning(f"Templates root {self.templates_root} does not exist.")
            return templates

        for name in os.listdir(self.templates_root):
            template_path = os.path.join(self.templates_root, name)
            if os.path.isdir(template_path):
                metadata_path = os.path.join(template_path, "metadata.json")
                if os.path.exists(metadata_path):
                    try:
                        with open(metadata_path, 'r') as f:
                            metadata = json.load(f)
                            metadata["id"] = name
                            metadata["path"] = template_path
                            templates[name] = metadata
                    except Exception as e:
                        self.logger.error(f"Error loading metadata for {name}: {e}")
        return templates

    def list_templates(self) -> List[Dict[str, Any]]:
        """Returns a list of all available templates."""
        return list(self.templates.values())

    def match_template(self, goal: str) -> Optional[Dict[str, Any]]:
        """
        Matches a user goal to the most appropriate template.
        Uses simple keyword matching for now, but can be upgraded to LLM-based matching.
        """
        goal_lower = goal.lower()
        
        # Simple keyword-based matching
        scoring = {}
        for name, meta in self.templates.items():
            score = 0
            # Check name and description
            if name.lower() in goal_lower or meta.get("name", "").lower() in goal_lower:
                score += 5
            
            # Check tags
            for tag in meta.get("tags", []):
                if tag.lower() in goal_lower:
                    score += 3
            
            if score > 0:
                scoring[name] = score

        if scoring:
            # Return the highest scoring template
            best_match = max(scoring, key=scoring.get)
            return self.templates[best_match]
        
        return None

    def get_template_files(self, template_id: str) -> Dict[str, str]:
        """
        Returns a dictionary mapping file paths to their content for a given template.
        """
        template = self.templates.get(template_id)
        if not template:
            return {}

        files = {}
        
        # Check if 'structure' is defined in metadata.json (legacy/simple)
        if "structure" in template:
            files.update(template["structure"])
            
        # Check for a 'files' subdirectory (preferred)
        files_dir = os.path.join(template["path"], "files")
        if os.path.exists(files_dir):
            for root, _, filenames in os.walk(files_dir):
                for filename in filenames:
                    abs_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(abs_path, files_dir)
                    try:
                        with open(abs_path, 'r', encoding='utf-8') as f:
                            files[rel_path] = f.read()
                    except Exception as e:
                        self.logger.error(f"Error reading template file {rel_path}: {e}")
        
        return files

    def customize_template(self, files: Dict[str, str], user_needs: str) -> Dict[str, str]:
        """
        Placeholder for LLM-based customization.
        In a real scenario, this would use the LLM to modify the template files
        based on the specific user needs.
        """
        # For now, just return the original files.
        # Implementation would involve sending the user_needs and file content to LLM.
        return files

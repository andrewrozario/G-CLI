import os
import re
import logging
from typing import List, Dict, Any, Optional

class Skill:
    """Represents a parsed Gaia CLI skill."""
    def __init__(self, name: str, description: str, tags: List[str], tools: List[str], instructions: str, path: str):
        self.name = name
        self.description = description
        self.tags = [t.strip().lower() for t in tags]
        self.tools = [t.strip().lower() for t in tools]
        self.instructions = instructions
        self.path = path

class SkillLoader:
    """
    Recursively loads skills from the 'skills' directory.
    Parses Markdown headers to extract metadata.
    """
    def __init__(self, skills_root: str):
        self.skills_root = skills_root
        self.logger = logging.getLogger("SkillLoader")
        self.skills: List[Skill] = []
        self.load_all()

    def load_all(self):
        """Walks the directory and parses every .md skill file."""
        self.logger.info(f"Loading skills from: {self.skills_root}")
        for root, _, files in os.walk(self.skills_root):
            for file in files:
                if file.endswith(".md"):
                    skill_path = os.path.join(root, file)
                    skill = self._parse_md_skill(skill_path)
                    if skill:
                        self.skills.append(skill)
                        self.logger.debug(f"Loaded skill: {skill.name}")

    def _parse_md_skill(self, file_path: str) -> Optional[Skill]:
        """Parses a skill from its Markdown format."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract metadata using regex from headers
            name_match = re.search(r"^# SKILL:\s*(.*)$", content, re.MULTILINE)
            desc_match = re.search(r"^# DESCRIPTION:\s*(.*)$", content, re.MULTILINE)
            tags_match = re.search(r"^# TAGS:\s*(.*)$", content, re.MULTILINE)
            tools_match = re.search(r"^# REQUIRED_TOOLS:\s*(.*)$", content, re.MULTILINE)
            
            # Extract instructions (everything after the first ## header)
            instructions_match = re.search(r"## Specialized Instructions\n([\s\S]*)", content)

            if name_match:
                return Skill(
                    name=name_match.group(1).strip(),
                    description=desc_match.group(1).strip() if desc_match else "",
                    tags=tags_match.group(1).split(",") if tags_match else [],
                    tools=tools_match.group(1).split(",") if tools_match else [],
                    instructions=instructions_match.group(1).strip() if instructions_match else "",
                    path=file_path
                )
        except Exception as e:
            self.logger.error(f"Failed to parse skill at {file_path}: {e}")
        return None

class SkillSelector:
    """
    Selects relevant skills based on the task description.
    Supports basic keyword matching and tagging.
    """
    def __init__(self, loader: SkillLoader):
        self.loader = loader
        self.logger = logging.getLogger("SkillSelector")

    def find_skills(self, task_description: str) -> List[Skill]:
        """
        Scans the task for keywords and returns all matching skills.
        """
        task_lower = task_description.lower()
        selected = []
        
        for skill in self.loader.skills:
            # Check if any tag matches the task description
            if any(tag in task_lower for tag in skill.tags):
                selected.append(skill)
            # Or if the skill name is explicitly mentioned
            elif skill.name.lower() in task_lower:
                selected.append(skill)
                
        self.logger.info(f"Selected {len(selected)} skills for task: '{task_description}'")
        return selected

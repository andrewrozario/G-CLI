import os
import logging
from typing import Dict, Any, List, Optional
from gaia_cmd.core.prompt.orchestrator import PromptBuilder, PromptMode
from gaia_cmd.core.prompt.role_config import AgentRole
from gaia_cmd.core.skills.loader import SkillLoader, SkillSelector
from gaia_cmd.core.learning.refiner import SelfImprovementManager
from gaia_cmd.core.project.mapper import ProjectMapper

class CodebaseAnalyzer:
    """
    Summarizes the project structure to provide context for the AI.
    Used for 'codebase_summary' in PromptBuilder.
    """
    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root

    def get_summary(self, max_depth: int = 2) -> str:
        """Returns a simplified tree view of the workspace."""
        summary = ["Project Structure:"]
        for root, dirs, files in os.walk(self.workspace_root):
            depth = root.replace(self.workspace_root, '').count(os.sep)
            if depth >= max_depth:
                continue
            
            indent = "  " * depth
            summary.append(f"{indent}{os.path.basename(root)}/")
            for f in files[:10]: # Limit files per dir to avoid bloating
                if not f.startswith('.'):
                    summary.append(f"  {indent}{f}")
        return "\n".join(summary)

class PromptOrchestrator:
    """
    High-level facade that integrates Memory, Tools, Skills, Codebase Analysis, 
    Self-Improvement lessons, and Project Intelligence into the dynamic PromptBuilder.
    """
    def __init__(self, workspace_root: str, memory_manager: Any, tool_executor: Any):
        self.workspace_root = workspace_root
        self.memory = memory_manager
        self.tools = tool_executor
        
        # Skills System
        self.skills_root = os.path.join(workspace_root, "skills")
        self.loader = SkillLoader(self.skills_root)
        self.selector = SkillSelector(self.loader)
        
        # Self-Improvement System
        self.improvement = SelfImprovementManager(workspace_root)
        
        # Project Intelligence Engine
        self.project_mapper = ProjectMapper(workspace_root)
        
        self.builder = PromptBuilder(workspace_root)
        self.analyzer = CodebaseAnalyzer(workspace_root)
        self.logger = logging.getLogger("PromptOrchestrator")

    def get_task_payload(self, task: str, mode: PromptMode = PromptMode.CODING, agent_role: Optional[AgentRole] = None) -> List[Dict[str, str]]:
        """
        Gathers all dynamic context and returns the complete LLM message list.
        Now includes 'Skills', 'Self-Improvement', 'Project Intelligence', and 'Agent Role' injection.
        """
        self.logger.info(f"Assembling prompt payload for task: {task} in mode: {mode.value}")
        
        # 1. Fetch relevant memory context
        memory_context = self.memory.build_prompt_context(task)
        
        # 2. Fetch available tool schemas
        tool_schemas = self.tools.get_available_tools_schema()
        
        # 3. Get codebase summary (static tree)
        codebase_summary = self.analyzer.get_summary()
        
        # 4. Get project intelligence (dynamic architecture summary)
        project_intelligence = self.project_mapper.get_summary_for_prompt()
        
        # 5. Select and format skills
        active_skills = self.selector.find_skills(task)
        skills_instructions = self._format_skills_instructions(active_skills)
        
        # 6. Fetch self-improvement lessons
        behavioral_adjustment = self.improvement.get_behavioral_adjustment()
        
        # 7. Build final message list
        base_messages = self.builder.build_full_prompt(
            mode=mode,
            task=task,
            memory_context=memory_context,
            tool_schemas=tool_schemas,
            codebase_summary=codebase_summary,
            agent_role=agent_role
        )
        
        # Inject skills and improvement lessons into the system message content
        system_message_content = base_messages[0]['content']
        
        # Append Project Intelligence
        system_message_content += f"\n\n{project_intelligence}"
        
        if skills_instructions:
            system_message_content += f"\n\n### ACTIVATED SKILLS ###\n{skills_instructions}"
            
        if behavioral_adjustment:
            system_message_content += behavioral_adjustment
            
        base_messages[0]['content'] = system_message_content
            
        return base_messages

    def _format_skills_instructions(self, skills: List[Any]) -> str:
        """Formats the specialized instructions from all selected skills."""
        if not skills:
            return ""
        
        formatted = []
        for skill in skills:
            formatted.append(f"#### SKILL: {skill.name} ####")
            formatted.append(skill.instructions)
        return "\n\n".join(formatted)

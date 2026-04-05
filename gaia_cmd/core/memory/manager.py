import logging
import os
from typing import Any, Dict, List, Optional
from gaia_cmd.core.memory.short_term import ShortTermMemory
from gaia_cmd.core.memory.long_term import LongTermMemory
from gaia_cmd.core.memory.global_memory import GlobalMemory
from gaia_cmd.core.memory.persistent_memory import PersistentMemory

class MemoryManager:
    """
    Advanced Memory Manager (Deep Learning Mode).
    Handles short-term session state, project-specific memory, 
    persistent global cross-project knowledge, and infinite context JSON stores.
    """
    def __init__(self, workspace_root: str):
        self.logger = logging.getLogger("MemoryManager")
        self.workspace_root = workspace_root
        self.short_term = ShortTermMemory()
        self.long_term = LongTermMemory(workspace_root)
        self.global_memory = GlobalMemory()
        
        # Infinite Context Subsystem
        memory_data_dir = os.path.join(workspace_root, "gaia_cmd", "memory")
        self.persistent = PersistentMemory(memory_data_dir)
        
        self.project_name = os.path.basename(workspace_root)

    def build_prompt_context(self, current_task: str) -> str:
        """
        Retrieves context from all levels of memory for prompt injection.
        Includes cross-project patterns, session history, and infinite context stores.
        """
        self.short_term.set_task(current_task)
        st_context = self.short_term.get_context()
        recent_actions_str = "\n".join([f"- {a['action']}: {a['result']}" for a in st_context['recent_actions']])
        
        # 1. Fetch Global/Local Knowledge
        global_knowledge_str = self.global_memory.get_context_for_prompt(current_task, limit=3)
        lt_results = self.long_term.search(current_task, limit=2)
        lt_knowledge_str = "\n".join(lt_results) if lt_results else "No specific project rules found."
        
        # 2. Fetch Infinite Context (JSON Stores)
        infinite_context = self.persistent.get_infinite_context(current_task)

        context = f"""
### INFINITE CONTEXT (Historical Records) ###
{infinite_context}

### GLOBAL KNOWLEDGE (Deep Learning) ###
{global_knowledge_str}

### PROJECT CONTEXT (Local to {self.project_name}) ###
{lt_knowledge_str}

### SESSION STATE (Short-term) ###
Active Files: {', '.join(st_context['active_files']) or 'None'}
Recent Actions:
{recent_actions_str or 'None'}
"""
        return context

    def record_action(self, action: str, result: str):
        self.short_term.add_action(action, result)

    def learn_from_feedback(self, task: str, success: bool, diagnosis: str = "", tags: List[str] = None):
        """
        Deep Learning logic: Automatically persists insights to global and persistent memory.
        """
        category = "solution" if success else "mistake"
        insight = f"Task: {task}. {'Completed successfully' if success else 'Failed'}. "
        if diagnosis:
            insight += f"Insight: {diagnosis}"
        
        # Save to Infinite Context Store
        self.persistent.save_task(task, diagnosis or "Task completed", success)
        
        # Persist to Global Memory
        self.global_memory.add_entry(
            content=insight,
            category=category,
            tags=tags or [self.project_name, task.split()[0].lower()],
            success=success,
            project=self.project_name
        )
        
        # Local copy if architectural
        if "architecture" in (tags or []):
            self.long_term.add_insight("architecture", insight)
            self.persistent.save_pattern(f"Arch: {task}", diagnosis, self.project_name)

    def add_insight(self, category: str, insight: str, tags: List[str] = None):
        """Manually add an insight."""
        self.global_memory.add_entry(
            content=insight,
            category=category,
            tags=tags or ["manual"],
            project=self.project_name
        )
        if category == "pattern":
            self.persistent.save_pattern("Manual Pattern", insight, "manual")

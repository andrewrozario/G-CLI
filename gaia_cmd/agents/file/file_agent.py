import os
import shutil
import logging
from typing import Any, Dict, List, Optional
from gaia_cmd.agents.builder.builder import BuilderAgent
from gaia_cmd.core.llm.provider import LLMProvider
from gaia_cmd.tools.executor.executor import ToolExecutor
from gaia_cmd.core.prompt.manager import PromptOrchestrator
from gaia_cmd.core.prompt.role_config import AgentRole
from gaia_cmd.core.communication.message import Message

class FileAgent(BuilderAgent):
    """
    Specialized agent for robust file and directory operations.
    Focuses on cloning projects, branding removal, and asset injection.
    """
    def __init__(self, llm: LLMProvider, executor: ToolExecutor, prompt_engine: PromptOrchestrator):
        super().__init__(llm, executor, prompt_engine, name="file_agent", role=AgentRole.FILE)
        self.description = "Specialized in project cloning, branding removal, and filesystem management"

    def process_message(self, message: Message) -> Message:
        content = message.content
        action = content.get("action")
        
        try:
            if action == "copy_directory":
                res = self.copy_directory(content.get("source"), content.get("destination"))
                return self.send_message(message.sender, res, message.task_id)
            
            elif action == "replace_text":
                res = self.replace_text(content.get("directory"), content.get("old"), content.get("new"))
                return self.send_message(message.sender, res, message.task_id)
            
            elif action == "replace_file":
                res = self.replace_file(content.get("target_path"), content.get("new_file_path"))
                return self.send_message(message.sender, res, message.task_id)
            
            elif action == "rename_files":
                res = self.rename_files(content.get("directory"), content.get("old_name"), content.get("new_name"))
                return self.send_message(message.sender, res, message.task_id)
            
            return super().process_message(message)
        except Exception as e:
            self.logger.error(f"FileAgent operation failed: {e}")
            return self.send_message(message.sender, {"success": False, "error": str(e)}, message.task_id)

    def copy_directory(self, src: str, dst: str) -> Dict[str, Any]:
        """Clones an entire directory substrate."""
        src_path = os.path.join(self.executor.workspace_root, src)
        dst_path = os.path.join(self.executor.workspace_root, dst)
        
        self.logger.info(f"Cloning substrate: {src} -> {dst}")
        shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
        return {"success": True, "output": f"Successfully manifested clone at {dst}"}

    def replace_text(self, directory: str, old: str, new: str) -> Dict[str, Any]:
        """Scans and replaces text sequences across the project."""
        root_dir = os.path.join(self.executor.workspace_root, directory)
        self.logger.info(f"Initiating branding removal: {old} -> {new} in {directory}")
        
        modified_count = 0
        for root, _, files in os.walk(root_dir):
            for file in files:
                file_path = os.path.join(root, file)
                if self._is_binary(file_path):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    if old in content:
                        new_content = content.replace(old, new)
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        modified_count += 1
                except Exception as e:
                    self.logger.warning(f"Could not process {file_path}: {e}")

        return {"success": True, "output": f"Harmonized {modified_count} files. Branding '{old}' removed."}

    def replace_file(self, target_path: str, new_file_path: str) -> Dict[str, Any]:
        """Injects a specific file (e.g., a new logo)."""
        dst = os.path.join(self.executor.workspace_root, target_path)
        src = os.path.join(self.executor.workspace_root, new_file_path)
        
        self.logger.info(f"Injecting asset: {new_file_path} -> {target_path}")
        shutil.copy2(src, dst)
        return {"success": True, "output": f"Asset {target_path} stabilized with new source."}

    def rename_files(self, directory: str, old_name: str, new_name: str) -> Dict[str, Any]:
        """Renames files matching a pattern within a directory."""
        root_dir = os.path.join(self.executor.workspace_root, directory)
        renamed_count = 0
        
        for root, _, files in os.walk(root_dir):
            for file in files:
                if old_name in file:
                    old_path = os.path.join(root, file)
                    new_file_name = file.replace(old_name, new_name)
                    new_path = os.path.join(root, new_file_name)
                    os.rename(old_path, new_path)
                    renamed_count += 1
                    
        return {"success": True, "output": f"Evolved {renamed_count} file identities."}

    def _is_binary(self, file_path: str) -> bool:
        """Heuristic to skip binary files during text replacement."""
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                return b'\0' in chunk
        except:
            return True

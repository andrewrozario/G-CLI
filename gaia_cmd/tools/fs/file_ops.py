import os
from typing import Any, Dict
from gaia_cmd.core.tools.base import BaseTool

class ReadFileTool(BaseTool):
    name = "read_file"
    description = "Reads the contents of a specified file."
    parameters_schema = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Relative path to the file."}
        },
        "required": ["path"]
    }

    def __init__(self, workspace_root: str):
        super().__init__()
        self.workspace_root = workspace_root

    def _run(self, path: str) -> str:
        full_path = os.path.join(self.workspace_root, path)
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"File not found: {path}")
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()

class WriteFileTool(BaseTool):
    name = "write_file"
    description = "Writes complete content to a file, creating it and parent directories if they don't exist. Overwrites existing files."
    parameters_schema = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Relative path to the file."},
            "content": {"type": "string", "description": "The complete content to write."}
        },
        "required": ["path", "content"]
    }

    def __init__(self, workspace_root: str):
        super().__init__()
        self.workspace_root = workspace_root

    def _run(self, path: str, content: str) -> str:
        full_path = os.path.join(self.workspace_root, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {path}"

class EditFileTool(BaseTool):
    name = "edit_file"
    description = "Replaces a specific exact string in a file with a new string. Fails if the string is not found."
    parameters_schema = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Relative path to the file."},
            "old_string": {"type": "string", "description": "The exact literal text to replace."},
            "new_string": {"type": "string", "description": "The text to replace it with."}
        },
        "required": ["path", "old_string", "new_string"]
    }

    def __init__(self, workspace_root: str):
        super().__init__()
        self.workspace_root = workspace_root

    def _run(self, path: str, old_string: str, new_string: str) -> str:
        full_path = os.path.join(self.workspace_root, path)
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"File not found: {path}")
            
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if old_string not in content:
            raise ValueError(f"Target string '{old_string}' not found in {path}. Edit failed.")
            
        new_content = content.replace(old_string, new_string, 1) # Only replace first exact match by default for safety
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return f"Successfully edited {path}"

class CopyDirectoryTool(BaseTool):
    name = "copy_directory"
    description = "Copies an entire directory from source to destination."
    parameters_schema = {
        "type": "object",
        "properties": {
            "source": {"type": "string", "description": "Source path."},
            "destination": {"type": "string", "description": "Destination path."}
        },
        "required": ["source", "destination"]
    }

    def __init__(self, workspace_root: str):
        super().__init__()
        self.workspace_root = workspace_root

    def _run(self, source: str, destination: str) -> str:
        import shutil
        src_full = os.path.join(self.workspace_root, source)
        dst_full = os.path.join(self.workspace_root, destination)
        shutil.copytree(src_full, dst_full, dirs_exist_ok=True)
        return f"Successfully copied {source} to {destination}"

class RenameFileTool(BaseTool):
    name = "rename_file"
    description = "Renames or moves a file/directory."
    parameters_schema = {
        "type": "object",
        "properties": {
            "old_path": {"type": "string", "description": "Current path."},
            "new_path": {"type": "string", "description": "New path."}
        },
        "required": ["old_path", "new_path"]
    }

    def __init__(self, workspace_root: str):
        super().__init__()
        self.workspace_root = workspace_root

    def _run(self, old_path: str, new_path: str) -> str:
        old_full = os.path.join(self.workspace_root, old_path)
        new_full = os.path.join(self.workspace_root, new_path)
        os.rename(old_full, new_full)
        return f"Successfully renamed {old_path} to {new_path}"

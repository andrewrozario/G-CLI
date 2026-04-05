import os
import shutil
import difflib

class FileManager:
    """Handles all file system operations for G CLI."""
    
    def read_file(self, file_path: str) -> str:
        if not os.path.exists(file_path):
            return f"Error: File {file_path} not found."
        with open(file_path, 'r') as f:
            return f.read()

    def write_file(self, file_path: str, content: str, backup: bool = True) -> str:
        if backup and os.path.exists(file_path):
            backup_path = file_path + ".gcli_backup"
            shutil.copy2(file_path, backup_path)
        
        with open(file_path, 'w') as f:
            f.write(content)
        return f"Successfully wrote to {file_path}"

    def list_files(self, directory: str = ".") -> list:
        files = []
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                files.append(os.path.join(root, filename))
        return files

    def get_diff(self, file_path: str, new_content: str) -> str:
        old_content = self.read_file(file_path).splitlines()
        new_content_lines = new_content.splitlines()
        diff = difflib.unified_diff(old_content, new_content_lines, fromfile=file_path, tofile=file_path + " (new)")
        return "\n".join(list(diff))

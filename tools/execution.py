import subprocess
import os

def execute_shell(command: str) -> str:
    try:
        result = subprocess.run(
            command, shell=True, check=True, 
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"

def read_file(filepath: str) -> str:
    if not os.path.exists(filepath):
        return "File not found."
    with open(filepath, "r") as f:
        return f.read()

def write_to_file(filepath: str, content: str) -> str:
    with open(filepath, "w") as f:
        f.write(content)
    return f"Successfully wrote to {filepath}"

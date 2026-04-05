import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from rich.console import Console

class GCLIHandler(FileSystemEventHandler):
    def __init__(self, on_change_callback):
        self.on_change_callback = on_change_callback
        self.last_triggered = 0
        self.debounce_seconds = 2 # Prevent rapid double-triggers

    def on_modified(self, event):
        if event.is_directory:
            return
        
        # Ignore common noise
        ignored = ['.git', '__pycache__', 'node_modules', 'venv', '.gaia_memory', '.bak']
        if any(x in event.src_path for x in ignored):
            return

        current_time = time.time()
        if current_time - self.last_triggered > self.debounce_seconds:
            self.last_triggered = current_time
            self.on_change_callback(event.src_path)

class FileWatcher:
    """Foundational watcher system using watchdog."""
    def __init__(self, path, on_change):
        self.path = path
        self.on_change = on_change
        self.console = Console()

    def start(self):
        self.console.print(f"\n👁  [bold cyan]Continuous Mode Active:[/bold cyan] Watching {self.path}...")
        event_handler = GCLIHandler(self.on_change)
        observer = Observer()
        observer.schedule(event_handler, self.path, recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

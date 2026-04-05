import threading
from typing import Dict, Set

class LockManager:
    """
    Manages fine-grained locks for files and directories to prevent
    conflicts during parallel agent execution.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(LockManager, cls).__new__(cls)
                cls._instance.locks: Dict[str, threading.Lock] = {}
                cls._instance.active_locks: Set[str] = set()
            return cls._instance

    def get_lock(self, resource_path: str) -> threading.Lock:
        """
        Returns a threading lock for a specific file or resource path.
        """
        with self._lock:
            if resource_path not in self.locks:
                self.locks[resource_path] = threading.Lock()
            return self.locks[resource_path]

    def is_locked(self, resource_path: str) -> bool:
        """Checks if a resource is currently locked by any agent."""
        return resource_path in self.active_locks

    def acquire(self, resource_path: str):
        """Acquires a lock for a resource."""
        lock = self.get_lock(resource_path)
        lock.acquire()
        with self._lock:
            self.active_locks.add(resource_path)

    def release(self, resource_path: str):
        """Releases a lock for a resource."""
        lock = self.get_lock(resource_path)
        if lock.locked():
            lock.release()
        with self._lock:
            if resource_path in self.active_locks:
                self.active_locks.remove(resource_path)

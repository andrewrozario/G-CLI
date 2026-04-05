import concurrent.futures
import logging
from typing import List, Callable, Any, Dict
from gaia_cmd.core.execution.locks import LockManager

class ParallelExecutionEngine:
    """
    Parallel Execution System for Gaia CLI.
    Enables multiple agents to work simultaneously on different modules.
    Includes conflict resolution and synchronization layer.
    """
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.logger = logging.getLogger("ParallelExecution")
        self.lock_manager = LockManager()

    def execute_in_parallel(self, tasks: List[Dict[str, Any]], execute_fn: Callable[[Any], bool]) -> Dict[str, bool]:
        """
        Executes multiple task steps in parallel using a thread pool.
        'tasks' should be a list of TaskStep objects or similar.
        'execute_fn' is the function that performs the actual agent execution.
        """
        results = {}
        
        # 1. Conflict Resolution: Filter tasks that can be run safely in parallel
        safe_to_run = self._resolve_conflicts(tasks)
        
        if not safe_to_run:
            self.logger.warning("No tasks are currently safe to run in parallel due to resource conflicts.")
            return results

        self.logger.info(f"Distributing {len(safe_to_run)} tasks across {self.max_workers} parallel workers.")

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Create a mapping of future to task ID
            future_to_task_id = {
                executor.submit(execute_fn, task): task.id for task in safe_to_run
            }
            
            for future in concurrent.futures.as_completed(future_to_task_id):
                task_id = future_to_task_id[future]
                try:
                    success = future.result()
                    results[task_id] = success
                except Exception as e:
                    self.logger.error(f"Parallel task {task_id} failed with error: {e}")
                    results[task_id] = False

        return results

    def _resolve_conflicts(self, tasks: List[Any]) -> List[Any]:
        """
        Identifies and resolves resource conflicts between tasks.
        If two tasks require the same files, only one is scheduled for the current parallel batch.
        """
        safe_tasks = []
        locked_files = set()

        for task in tasks:
            # We assume TaskStep has 'required_files' or similar metadata
            required_files = getattr(task, 'required_files', [])
            
            has_conflict = False
            for file_path in required_files:
                if file_path in locked_files:
                    has_conflict = True
                    break
            
            if not has_conflict:
                safe_tasks.append(task)
                # Reserve these files for this parallel batch
                for file_path in required_files:
                    locked_files.add(file_path)
            else:
                self.logger.info(f"Postponing task {task.id} due to file conflict with another parallel task.")

        return safe_tasks

import os
import logging
from typing import List, Dict, Any, Optional

class GaiaVerifier:
    """
    Verification Layer for Gaia CLI.
    Ensures that planned manifestations are empirically present in the physical substrate.
    Eliminates false success reports by performing real-world validation.
    """
    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root
        self.logger = logging.getLogger("GaiaVerifier")

    def verify_directory_exists(self, path: str) -> bool:
        """Confirms existence of a directory substrate."""
        full_path = os.path.join(self.workspace_root, path)
        exists = os.path.isdir(full_path)
        if not exists:
            self.logger.warning(f"Verification Failed: Substrate directory {path} not found.")
        return exists

    def verify_file_exists(self, path: str) -> bool:
        """Confirms existence of a specific file entity."""
        full_path = os.path.join(self.workspace_root, path)
        exists = os.path.isfile(full_path)
        if not exists:
            self.logger.warning(f"Verification Failed: File entity {path} not found.")
        return exists

    def verify_text_replaced(self, directory: str, keyword: str, forbidden_keyword: Optional[str] = None) -> bool:
        """
        Scans a directory substrate to ensure a keyword exists 
        and optionally ensures a forbidden keyword is purged.
        """
        root_dir = os.path.join(self.workspace_root, directory)
        if not os.path.exists(root_dir):
            self.logger.error(f"Cannot verify text: Directory {directory} does not exist.")
            return False

        found_new = False
        for root, _, files in os.walk(root_dir):
            for file in files:
                file_path = os.path.join(root, file)
                # Skip binary files
                if self._is_binary(file_path):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    if forbidden_keyword and forbidden_keyword in content:
                        self.logger.warning(f"Verification Failed: Forbidden keyword '{forbidden_keyword}' still present in {file_path}.")
                        return False
                    
                    if keyword in content:
                        found_new = True
                except Exception as e:
                    self.logger.debug(f"Skipping file {file_path} during verification: {e}")

        if not found_new:
            self.logger.warning(f"Verification Failed: Target keyword '{keyword}' not found in substrate {directory}.")
            return False
            
        return True

    def run_empirical_check(self, step_type: str, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for real-world validation.
        Rules:
        - If verification fails, return success=False.
        - Triggers DebugAgent via the Execution Engine.
        """
        self.logger.info(f"Initiating empirical check for type: {step_type}")
        
        try:
            success = False
            error_msg = "Empirical state mismatch"

            if step_type == "file_operation":
                path = criteria.get("path")
                if path:
                    if os.path.isdir(os.path.join(self.workspace_root, path)):
                        success = self.verify_directory_exists(path)
                    else:
                        success = self.verify_file_exists(path)
                
                # Check for specific text if provided
                if "keyword" in criteria:
                    success = self.verify_text_replaced(
                        criteria.get("directory", "."), 
                        criteria["keyword"],
                        criteria.get("forbidden_keyword")
                    )
            
            elif step_type == "branding":
                success = self.verify_text_replaced(
                    criteria.get("directory", "."),
                    criteria.get("new_brand", ""),
                    criteria.get("old_brand")
                )

            else:
                # Default safety check: verify all requested files exist
                req_files = criteria.get("required_files", [])
                if req_files:
                    success = all(self.verify_file_exists(f) for f in req_files)
                else:
                    success = True # No criteria to verify

            return {
                "success": success,
                "error": None if success else error_msg
            }
            
        except Exception as e:
            self.logger.error(f"Verification Engine Error: {e}")
            return {"success": False, "error": str(e)}

    def _is_binary(self, file_path: str) -> bool:
        """Helper to identify binary files."""
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                return b'\0' in chunk
        except:
            return True

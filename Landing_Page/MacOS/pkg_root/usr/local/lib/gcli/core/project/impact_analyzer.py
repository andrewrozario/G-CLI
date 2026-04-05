import os

class ImpactAnalyzer:
    """Analyzes the dependency graph to predict which files will break if a target is modified."""
    
    def find_impacted_files(self, graph: dict, target_files: list) -> list:
        impacted = []
        
        for target in target_files:
            target_name = os.path.basename(target).split('.')[0]
            
            for file_path, data in graph.items():
                if file_path in target_files:
                    continue
                    
                # Check if this file imports the target file or its name
                for imp in data.get("imports", []):
                    if target_name in imp or target in imp:
                        if file_path not in impacted:
                            impacted.append(file_path)
                            
        return impacted

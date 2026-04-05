import os
import re

class DependencyGraph:
    """Maps imports and exports to understand project-wide relationships."""
    
    def build(self, files: list) -> dict:
        graph = {}
        for file_path in files:
            if not os.path.isfile(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Regex for common import patterns (Python, JS/TS)
                # Matches: import { x } from './path' or from x import y
                import_patterns = [
                    r"import .* from ['\"](.*)['\"]",
                    r"from (.*) import",
                    r"require\(['\"](.*)['\"]\)"
                ]
                
                imports = []
                for pattern in import_patterns:
                    matches = re.findall(pattern, content)
                    imports.extend(matches)
                
                graph[file_path] = {
                    "imports": imports,
                    "exports": re.findall(r"export (?:function|const|class|default)", content)
                }
            except:
                continue
        return graph

import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from memory.vector_db import VectorMemory
from system.file_manager import FileManager
from core.structural_analyzer import StructuralAnalyzer
from memory.long_term_memory import IntelligenceSummarizer

class CodebaseIngestor:
    """Maximizes G CLI's RAG by ingesting entire projects with structural and hierarchical context."""
    def __init__(self, memory: VectorMemory, llm_client=None):
        self.memory = memory
        self.analyzer = StructuralAnalyzer()
        self.file_manager = FileManager()
        self.summarizer = IntelligenceSummarizer(llm_client) if llm_client else None
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=300,
            add_start_index=True
        )

    def ingest_directory(self, dir_path: str, ignore_dirs: list = [".git", "node_modules", "venv", "__pycache__"]):
        """Recursively reads, analyzes structurally, and indexes a local project into knowledge, reasoning, and architecture spaces."""
        file_summaries = {}
        for root, dirs, files in os.walk(dir_path):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            for file in files:
                if file.endswith(('.py', '.js', '.ts', '.go', '.rs', '.md', '.txt')):
                    file_path = os.path.join(root, file)
                    content = self.file_manager.read_file(file_path)
                    
                    if not content or content == "File not found.":
                        continue

                    # 1. Structural Analysis (AST-like)
                    self.analyzer.analyze_file(file_path, content)
                    
                    # 2. Hierarchical Summarization & Deep Intelligence
                    if self.summarizer:
                        # Extract basic summary -> Knowledge Collection
                        summary = self.summarizer.summarize_file(file_path, content)
                        file_summaries[file_path] = summary
                        self.memory.add_memory(
                            text=f"Summary of {file_path}: {summary}",
                            metadata={"type": "summary", "file": file_path},
                            doc_id=f"summary_{file_path}",
                            collection_name="knowledge"
                        )
                        
                        # Extract reasoning -> Reasoning Collection
                        reasoning = self.summarizer.extract_reasoning(file_path, content)
                        self.memory.add_memory(
                            text=f"Reasoning for {file_path}:\n{reasoning}",
                            metadata={"type": "reasoning", "file": file_path},
                            doc_id=f"reasoning_{file_path}",
                            collection_name="reasoning"
                        )
                        
                        # Extract architecture -> Architecture Collection
                        architecture = self.summarizer.extract_architecture(file_path, content)
                        self.memory.add_memory(
                            text=f"Architecture for {file_path}:\n{architecture}",
                            metadata={"type": "architecture", "file": file_path},
                            doc_id=f"arch_{file_path}",
                            collection_name="architecture"
                        )

                    # 3. Vector Ingestion (Standard RAG) -> Knowledge Collection
                    chunks = self.splitter.split_text(content)
                    for i, chunk in enumerate(chunks):
                        metadata = {
                            "source": file_path,
                            "filename": file,
                            "chunk": i,
                            "type": "code"
                        }
                        doc_id = f"{file_path}_{i}"
                        self.memory.add_memory(chunk, metadata, doc_id, collection_name="knowledge")
        
        return f"Successfully ingested {dir_path} into knowledge, reasoning, and architecture substrates."

    def ingest_github_repo(self, repo_url: str):
        """Clones a GitHub repo temporarily and ingests it."""
        import subprocess
        tmp_dir = "/tmp/gaia_ingest"
        try:
            subprocess.run(f"git clone --depth 1 {repo_url} {tmp_dir}", shell=True, check=True)
            result = self.ingest_directory(tmp_dir)
            subprocess.run(f"rm -rf {tmp_dir}", shell=True, check=True)
            return result
        except Exception as e:
            return f"Failed to ingest GitHub repo: {e}"

import json
import os
from models.base_client import BaseModelClient

class IntelligenceSummarizer:
    """Compresses files into hierarchical summaries (File -> Module -> Architecture) and extracts reasoning patterns."""
    
    def __init__(self, llm: BaseModelClient):
        self.llm = llm
        self.summaries = {} # memory_store

    def summarize_file(self, file_path: str, content: str) -> str:
        prompt = f"File: {file_path}\nContent:\n{content}\n\nSummarize the purpose, key functions, and dependencies of this file in 3 sentences."
        summary = self.llm.generate(prompt, system="You are an expert software architect. Provide dense, technical summaries.")
        self.summaries[file_path] = summary
        return summary

    def extract_reasoning(self, file_path: str, content: str) -> str:
        prompt = f"File: {file_path}\nContent:\n{content}\n\nExtract the core reasoning, design decisions, and implicit knowledge from this code. What problems does it solve, and why was it written this way?"
        reasoning = self.llm.generate(prompt, system="You are an expert software architect analyzing code reasoning.")
        return reasoning

    def extract_architecture(self, file_path: str, content: str) -> str:
        prompt = f"File: {file_path}\nContent:\n{content}\n\nDescribe the architectural patterns, data flow, and structural design present in this file."
        architecture = self.llm.generate(prompt, system="You are an expert software architect analyzing system structure.")
        return architecture

    def summarize_module(self, module_path: str, file_summaries: dict) -> str:
        all_summaries = "\n".join([f"{f}: {s}" for f, s in file_summaries.items()])
        prompt = f"Module: {module_path}\nFile Summaries:\n{all_summaries}\n\nSummarize the overall architectural purpose of this module."
        summary = self.llm.generate(prompt, system="You are an expert software architect.")
        self.summaries[module_path] = summary
        return summary

class LearningLoop:
    """Stores successful reasoning patterns and critiques to improve future responses."""
    
    def __init__(self, llm: BaseModelClient, db_path: str = "./.gaia_memory/learning_loop.json"):
        self.llm = llm
        self.db_path = db_path
        self.patterns = self._load_patterns()

    def _load_patterns(self) -> list:
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []

    def record_success(self, objective: str, execution_log: str):
        """Uses Gemini to distill a successful execution into a reusable reasoning pattern."""
        prompt = f"Objective: {objective}\nExecution Log:\n{execution_log}\n\nExtract a 'Reasoning Pattern' from this success. What logic worked best? What should we do again next time? Keep it under 100 words."
        pattern = self.llm.generate(prompt, system="You are the G CLI Learning Engine. Distill raw execution into high-value reasoning patterns.")
        
        self.patterns.append({
            "objective": objective,
            "pattern": pattern,
            "timestamp": "latest"
        })
        
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with open(self.db_path, 'w') as f:
            json.dump(self.patterns[-50:], f, indent=2) # Keep last 50 best patterns

    def get_relevant_patterns(self, objective: str) -> str:
        """Retrieves past successful reasoning to inject into new prompts."""
        if not self.patterns:
            return "No prior patterns recorded yet."
            
        # For now, return the most recent patterns as context
        context = "\n### LEARNED REASONING PATTERNS ###\n"
        for p in self.patterns[-3:]:
            context += f"- Task: {p['objective']}\n  Pattern: {p['pattern']}\n"
        return context

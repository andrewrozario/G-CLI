import json
from typing import List, Dict
from core.llm_client import LocalLLMClient
from core.prompts import build_system_prompt

class SwarmAgent:
    def __init__(self, name: str, role: str, llm: LocalLLMClient):
        self.name = name
        self.role = role
        self.llm = llm

    def think(self, objective: str, context: str) -> str:
        prompt = f"Objective: {objective}\nContext: {context}\nProvide your specialized analysis as a {self.role}."
        return self.llm.generate(prompt, system=build_system_prompt(self.role, "chain_of_thought"))

class AgentSwarm:
    """Orchestrates specialized cognitive agents for deep architectural reasoning."""
    
    def __init__(self, llm: LocalLLMClient):
        self.llm = llm
        self.agents = {
            "architect": SwarmAgent("Architect", "software_architect", llm),
            "debugger": SwarmAgent("Debugger", "qa_engineer", llm),
            "perf": SwarmAgent("Optimizer", "performance_optimizer", llm),
            "security": SwarmAgent("Security", "security_engineer", llm),
            "refactor": SwarmAgent("Refactor", "backend_specialist", llm)
        }

    def solve(self, objective: str, context: str = "") -> str:
        # 1. Broad Consensus / Multi-Agent Analysis
        analyses = {}
        for name, agent in self.agents.items():
            analyses[name] = agent.think(objective, context)
            
        # 2. Synthesis Layer (The 'Brain' merging outputs)
        synthesis_prompt = f"Objective: {objective}\nPeer Analyses:\n"
        for name, analysis in analyses.items():
            synthesis_prompt += f"[{name.upper()}]: {analysis}\n\n"
        
        synthesis_prompt += "Synthesize these specialized viewpoints into one master strategic roadmap. Resolve any internal debates or contradictions."
        
        final_strategy = self.llm.generate(
            synthesis_prompt, 
            system=build_system_prompt("software_architect", "step_back")
        )
        
        return final_strategy

    def debate(self, objective: str, context: str) -> str:
        """Simulates a debate between agents before reaching a conclusion."""
        architect_view = self.agents["architect"].think(objective, context)
        security_critique = self.agents["security"].think(f"Critique this architectural plan for security flaws: {architect_view}", context)
        
        final_prompt = f"Objective: {objective}\nProposed: {architect_view}\nCritique: {security_critique}\nProvide a hardened final architecture."
        return self.llm.generate(final_prompt, system=build_system_prompt("software_architect", "first_principles"))

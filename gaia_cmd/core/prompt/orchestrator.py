from enum import Enum
from typing import Any, Dict, List, Optional
from gaia_cmd.core.prompt.role_config import RoleConfig, AgentRole

class PromptMode(Enum):
    CODING = "coding"
    DEBUGGING = "debugging"
    ARCHITECTURE = "architecture"
    OPTIMIZATION = "optimization"

class SystemPrompts:
    """
    Static repository of base identity and behavior instructions for each mode.
    Ensures consistent 'persona' regardless of the specific task.
    """
    
    BASE = (
        "You are Gaia CLI, a senior AI systems architect and autonomous coding agent. "
        "Your goal is to execute tasks with surgical precision, maintaining high engineering standards. "
        "You always verify your work through tests and self-correction. "
        "Adhere strictly to the provided tool schemas and memory context."
    )

    MODES = {
        PromptMode.CODING: (
            "MODE: CODING. Focus on writing clean, idiomatic, and documented code. "
            "Prioritize readability and follow existing project patterns found in memory."
        ),
        PromptMode.DEBUGGING: (
            "MODE: DEBUGGING. You are in a high-diagnostic state. Analyze stack traces and error logs. "
            "Hypothesize root causes before applying fixes. Use 'rollback' if a fix introduces regressions."
        ),
        PromptMode.ARCHITECTURE: (
            "MODE: ARCHITECTURE. Focus on system design, decoupling, and interface definitions. "
            "Avoid implementation details; prioritize the 'why' and 'how' of the structural change."
        ),
        PromptMode.OPTIMIZATION: (
            "MODE: OPTIMIZATION. Focus on performance, memory footprint, and algorithmic efficiency. "
            "Profile before and after if possible. Ensure optimizations do not break existing logic."
        )
    }

class PromptBuilder:
    """
    The core orchestration engine. Dynamically assembles the full LLM payload.
    Combines Identity, Mode-specific rules, Memory, and Tool Instructions.
    """
    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root

    def build_system_message(self, mode: PromptMode) -> str:
        """Assembles the primary system instruction."""
        identity = SystemPrompts.BASE
        mode_rules = SystemPrompts.MODES.get(mode, SystemPrompts.MODES[PromptMode.CODING])
        
        return f"{identity}\n\n{mode_rules}\n\nAlways provide your reasoning before calling a tool."

    def build_tool_instructions(self, tool_schemas: List[Dict[str, Any]]) -> str:
        """Formats available tools into a clear instruction block for the LLM."""
        if not tool_schemas:
            return "No tools are currently available for this task."
            
        instructions = ["### AVAILABLE TOOLS ###", "You can use the following tools to interact with the environment:"]
        for tool in tool_schemas:
            instructions.append(f"- {tool['name']}: {tool['description']}")
            instructions.append(f"  Params: {tool['parameters'].get('properties', {})}")
            
        instructions.append("\nTo use a tool, respond with a JSON object in this format: {\"tool\": \"tool_name\", \"params\": { ... }}")
        return "\n".join(instructions)

    def build_context_block(self, memory_context: str, codebase_summary: Optional[str] = None) -> str:
        """Injects dynamic short/long term memory and file system state."""
        block = ["### CONTEXT INJECTION ###"]
        block.append(memory_context)
        
        if codebase_summary:
            block.append("\n### CODEBASE STATE ###")
            block.append(codebase_summary)
            
        return "\n".join(block)

    def build_full_prompt(self, 
                          mode: PromptMode, 
                          task: str, 
                          memory_context: str, 
                          tool_schemas: List[Dict[str, Any]], 
                          codebase_summary: Optional[str] = None,
                          agent_role: Optional[AgentRole] = None) -> List[Dict[str, str]]:
        """
        The main entry point: Returns a structured message list for LLM consumption.
        Now includes role-based intelligence.
        """
        system_content = self.build_system_message(mode)
        tool_content = self.build_tool_instructions(tool_schemas)
        context_content = self.build_context_block(memory_context, codebase_summary)
        
        # Inject Role Information if provided
        role_instruction = ""
        if agent_role:
            role_instruction = f"\n\n{RoleConfig.get_role_prompt(agent_role)}"
            
        # Combine instructions into the system role
        full_system_prompt = f"{system_content}{role_instruction}\n\n{context_content}\n\n{tool_content}"
        
        return [
            {"role": "system", "content": full_system_prompt},
            {"role": "user", "content": f"CURRENT TASK: {task}"}
        ]

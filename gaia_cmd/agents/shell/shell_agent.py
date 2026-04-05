from gaia_cmd.agents.builder.builder import BuilderAgent
from gaia_cmd.core.llm.provider import LLMProvider
from gaia_cmd.tools.executor.executor import ToolExecutor
from gaia_cmd.core.prompt.manager import PromptOrchestrator
from gaia_cmd.core.prompt.role_config import AgentRole

class ShellAgent(BuilderAgent):
    """
    Specialized agent for system commands, package management, and environment setup.
    Focuses on security and execution success.
    """
    def __init__(self, llm: LLMProvider, executor: ToolExecutor, prompt_engine: PromptOrchestrator):
        super().__init__(llm, executor, prompt_engine, name="shell_agent", role=AgentRole.SHELL)
        self.description = "Specialized in terminal commands and environment configuration"

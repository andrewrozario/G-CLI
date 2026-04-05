import logging
from typing import Any, Dict
from gaia_cmd.core.llm.provider import LLMProvider
from gaia_cmd.core.llm.safe_generate import safe_generate
from gaia_cmd.agents.base import BaseAgent
from gaia_cmd.core.communication.message import Message
from gaia_cmd.tools.executor.executor import ToolExecutor

class LearnerAgent(BaseAgent):
    """
    Autonomous Learning Agent.
    Triggered to research unknown concepts via the web, summarize findings,
    and structure reasoning data for ingestion.
    """
    def __init__(self, llm: LLMProvider, executor: ToolExecutor):
        super().__init__("learner", "Autonomous researcher that gathers architectural and reasoning knowledge from the web.")
        self.llm = llm
        self.executor = executor

    def process_message(self, message: Message) -> Message:
        content = message.content
        if not isinstance(content, dict):
            return self.send_message(message.sender, {"error": "Content must be a dict"}, message.task_id)

        action = content.get("action")
        try:
            if action == "research":
                topic = content.get("topic")
                findings = self.research_topic(topic)
                return self.send_message(message.sender, {"findings": findings}, message.task_id)
            else:
                return self.send_message(message.sender, {"error": f"Unknown action: {action}"}, message.task_id)
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            return self.send_message(message.sender, {"error": str(e)}, message.task_id)

    def research_topic(self, topic: str) -> str:
        """
        Uses the web_search tool to find information, then uses the LLM to extract reasoning.
        """
        self.logger.info(f"Learner Agent researching topic: {topic}")
        
        # 1. Search the web
        search_result = self.executor.execute_tool("web_search", {"query": f"{topic} architecture reasoning best practices"})
        
        if search_result.get("status") == "error":
            return f"Failed to research {topic}: {search_result.get('message')}"
            
        scraped_content = search_result.get("output", "")
        
        # 2. Analyze and summarize reasoning
        system_prompt = (
            "You are Gaia's Autonomous Learning Engine. Your job is to read raw documentation "
            "and extract 'Reasoning Data', 'Architectural Patterns', and 'Best Practices' "
            "that will make Gaia as powerful as Claude CLI."
        )
        
        user_prompt = (
            f"TOPIC: {topic}\n"
            f"SOURCE CONTENT:\n{scraped_content}\n\n"
            "Extract the core reasoning patterns, design decisions, and architectural strategies from this content."
        )
        
        try:
            response_data = safe_generate(self.llm, [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ], task_description=f"Researching: {topic}")
            
            return response_data.get("content", "No clear reasoning extracted.")
        except Exception as e:
            self.logger.error(f"Learner Agent LLM failure: {e}")
            return f"Partial findings from {topic}:\n{scraped_content[:500]}"

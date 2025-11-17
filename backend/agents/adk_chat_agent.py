import json
import asyncio
from typing import List, Dict, Any, Optional, AsyncGenerator
from datetime import datetime
import aioredis

from google.adk.agents.llm_agent import Agent
from google.adk.agent_config import AgentConfig
from google.adk.models import AgentOutput, ToolCode, ToolOutput

from ..chat_agent import ChatMemory # Reusing existing ChatMemory
from ..config import get_system_prompt, get_general_config, get_agent_config
from ..adk_tools import query_patient_by_id, query_patient_records


class AdkChatAgent:
    """
    Conversational AI agent with memory and tool usage capabilities,
    built using Google's Agent Development Kit (ADK).
    """

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        model: Optional[str] = None,
        temperature: Optional[float] = None
    ):
        self.memory = ChatMemory(redis_url)
        self.config = get_general_config()
        self.agent_config = get_agent_config('chat_agent')

        self.model = model or "gemini-2.5-flash" # Default to gemini-2.5-flash
        self.temperature = temperature or self.config['temperature']['chat_agent']
        self.max_tokens = self.config.get('max_tokens', 4096)

        self.system_prompt = get_system_prompt('chat_agent')

        # Define tools for the ADK agent
        self.tools = [
            query_patient_by_id,
            query_patient_records,
        ]

        # Initialize the ADK Agent
        self.adk_agent = Agent(
            model=self.model,
            name='ChatAgent',
            description='A helpful AI healthcare assistant for conversational tasks.',
            instruction=self.system_prompt,
            tools=self.tools,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            # Assuming ADK handles Vertex AI configuration internally via environment variables
            # or a dedicated config. If not, this will need adjustment.
        )

    async def chat(
        self,
        message: str,
        session_id: str,
        patient_id: Optional[str] = None,
        stream: bool = False
    ) -> AsyncGenerator[str, None]:
        """
        Process a chat message with streaming support using the ADK agent.
        """
        await self.memory.save_message(session_id, "user", message)
        history = await self.memory.get_history(session_id)

        # ADK agent expects messages in a specific format, typically a list of dicts
        # with 'role' and 'content'.
        adk_messages = []
        for msg in history:
            adk_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        context = await self.memory.get_context(session_id)
        if patient_id and patient_id != context.get('patient_id'):
            context['patient_id'] = patient_id
            await self.memory.save_context(session_id, context)

        full_response_content = ""

        async for agent_output in self.adk_agent.generate_response(
            messages=adk_messages,
            stream=True # Always stream from ADK agent, then handle external streaming
        ):
            if isinstance(agent_output, AgentOutput):
                if agent_output.text:
                    full_response_content += agent_output.text
                    if stream:
                        yield agent_output.text
                if agent_output.tool_code:
                    # ADK agent wants to call a tool
                    tool_code: ToolCode = agent_output.tool_code
                    tool_name = tool_code.name
                    tool_input = tool_code.args

                    tool_result = await self._execute_tool(tool_name, tool_input)

                    # Send tool output back to the agent
                    tool_output = ToolOutput(tool_code=tool_code, output=tool_result)
                    async for final_output in self.adk_agent.generate_response(
                        messages=adk_messages + [{"role": "assistant", "content": [tool_code.to_dict()]}, {"role": "user", "content": [tool_output.to_dict()]}],
                        stream=True
                    ):
                        if isinstance(final_output, AgentOutput) and final_output.text:
                            full_response_content += final_output.text
                            if stream:
                                yield final_output.text
            elif isinstance(agent_output, ToolOutput):
                # This case might occur if the agent directly returns tool output
                # without further text generation.
                # For now, we'll just log it or handle as needed.
                print(f"Received direct ToolOutput: {agent_output.output}")
                # If the tool output is the final response, we might need to yield it
                # or process it further. For now, assuming text is the primary output.

        if not stream:
            yield full_response_content

        await self.memory.save_message(session_id, "assistant", full_response_content)

    async def _execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Any:
        """Execute a tool call based on its name and input."""
        tool_function = next((t for t in self.tools if t.__name__ == tool_name), None)
        if tool_function:
            return await tool_function(**tool_input)
        else:
            return {"error": f"Unknown tool: {tool_name}"}

    async def get_welcome_message(self) -> str:
        """Get welcome message for new sessions"""
        return self.agent_config.get('welcome_message', 'Hello! How can I help you today?')

    async def clear_session(self, session_id: str):
        """Clear a chat session"""
        await self.memory.clear_history(session_id)

    async def close(self):
        """Cleanup resources"""
        await self.memory.disconnect()

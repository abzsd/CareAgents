"""
ChatAgent - Conversational AI agent with memory storage
"""
import json
import asyncio
from typing import List, Dict, Any, Optional, AsyncGenerator
from datetime import datetime
import anthropic
from redis import asyncio as aioredis

from .config import get_system_prompt, get_general_config, get_agent_config
from .tools.postgres_tools import TOOLS, query_patient_by_id, query_patient_records


class ChatMemory:
    """Redis-based chat memory storage"""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis: Optional[aioredis.Redis] = None

    async def connect(self):
        """Connect to Redis"""
        if self.redis is None:
            self.redis = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )

    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis:
            await self.redis.close()
            self.redis = None

    async def save_message(self, session_id: str, role: str, content: str):
        """Save a message to the conversation history"""
        await self.connect()
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        }
        key = f"chat:session:{session_id}"
        await self.redis.rpush(key, json.dumps(message))
        # Set expiry to 7 days
        await self.redis.expire(key, 604800)

    async def get_history(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve conversation history"""
        await self.connect()
        key = f"chat:session:{session_id}"
        messages = await self.redis.lrange(key, -limit, -1)
        return [json.loads(msg) for msg in messages]

    async def clear_history(self, session_id: str):
        """Clear conversation history for a session"""
        await self.connect()
        key = f"chat:session:{session_id}"
        await self.redis.delete(key)

    async def save_context(self, session_id: str, context: Dict[str, Any]):
        """Save session context (e.g., patient_id, user preferences)"""
        await self.connect()
        key = f"chat:context:{session_id}"
        await self.redis.set(key, json.dumps(context), ex=604800)

    async def get_context(self, session_id: str) -> Dict[str, Any]:
        """Retrieve session context"""
        await self.connect()
        key = f"chat:context:{session_id}"
        context = await self.redis.get(key)
        return json.loads(context) if context else {}


class ChatAgent:
    """
    Conversational AI agent with memory and tool usage capabilities
    """

    def __init__(
        self,
        api_key: str,
        redis_url: str = "redis://localhost:6379",
        model: Optional[str] = None,
        temperature: Optional[float] = None
    ):
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.memory = ChatMemory(redis_url)
        self.config = get_general_config()
        self.agent_config = get_agent_config('chat_agent')

        # Use config defaults if not specified
        self.model = model or self.config.get('model', 'claude-3-5-sonnet-20241022')
        self.temperature = temperature or self.config['temperature']['chat_agent']
        self.max_tokens = self.config.get('max_tokens', 4096)

        # System prompt
        self.system_prompt = get_system_prompt('chat_agent')

        # Available tools
        self.tools = TOOLS
        self.tool_functions = {
            'query_patient_by_id': query_patient_by_id,
            'query_patient_records': query_patient_records,
        }

    async def process_tool_call(self, tool_name: str, tool_input: Dict[str, Any]) -> Any:
        """Execute a tool call"""
        if tool_name in self.tool_functions:
            func = self.tool_functions[tool_name]
            return await func(**tool_input)
        else:
            return {"error": f"Unknown tool: {tool_name}"}

    async def chat(
        self,
        message: str,
        session_id: str,
        patient_id: Optional[str] = None,
        stream: bool = False
    ) -> AsyncGenerator[str, None]:
        """
        Process a chat message with streaming support

        Args:
            message: User's message
            session_id: Unique session identifier
            patient_id: Optional patient ID for context
            stream: Whether to stream the response

        Yields:
            Response chunks if streaming, otherwise yields complete response
        """
        # Save user message to memory
        await self.memory.save_message(session_id, "user", message)

        # Get conversation history
        history = await self.memory.get_history(session_id)

        # Build messages for Claude
        messages = []
        for msg in history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        # Get or update context
        context = await self.memory.get_context(session_id)
        if patient_id and patient_id != context.get('patient_id'):
            context['patient_id'] = patient_id
            await self.memory.save_context(session_id, context)

        # Make API call with streaming
        if stream:
            async with self.client.messages.stream(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self.system_prompt,
                messages=messages,
                tools=self.tools,
            ) as response_stream:
                full_response = ""
                tool_uses = []

                async for event in response_stream:
                    if hasattr(event, 'type'):
                        if event.type == 'content_block_start':
                            if hasattr(event, 'content_block') and hasattr(event.content_block, 'type'):
                                if event.content_block.type == 'tool_use':
                                    tool_uses.append({
                                        'id': event.content_block.id,
                                        'name': event.content_block.name,
                                        'input': {}
                                    })

                        elif event.type == 'content_block_delta':
                            if hasattr(event, 'delta'):
                                if hasattr(event.delta, 'type'):
                                    if event.delta.type == 'text_delta':
                                        chunk = event.delta.text
                                        full_response += chunk
                                        yield chunk
                                    elif event.delta.type == 'input_json_delta':
                                        # Tool input is being streamed
                                        if tool_uses:
                                            partial_json = event.delta.partial_json
                                            # Store for later processing
                                            pass

                        elif event.type == 'content_block_stop':
                            # Content block finished
                            pass

                        elif event.type == 'message_delta':
                            # Message-level delta
                            pass

                # Process tool calls if any
                if tool_uses:
                    # Get the final message to extract complete tool inputs
                    final_message = await response_stream.get_final_message()

                    tool_results = []
                    for content_block in final_message.content:
                        if content_block.type == 'tool_use':
                            tool_result = await self.process_tool_call(
                                content_block.name,
                                content_block.input
                            )
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": content_block.id,
                                "content": json.dumps(tool_result)
                            })

                    # If we have tool results, make another call to get the final response
                    if tool_results:
                        messages.append({
                            "role": "assistant",
                            "content": final_message.content
                        })
                        messages.append({
                            "role": "user",
                            "content": tool_results
                        })

                        # Second streaming call with tool results
                        async with self.client.messages.stream(
                            model=self.model,
                            max_tokens=self.max_tokens,
                            temperature=self.temperature,
                            system=self.system_prompt,
                            messages=messages,
                        ) as final_stream:
                            final_response = ""
                            async for event in final_stream:
                                if hasattr(event, 'type') and event.type == 'content_block_delta':
                                    if hasattr(event.delta, 'type') and event.delta.type == 'text_delta':
                                        chunk = event.delta.text
                                        final_response += chunk
                                        yield chunk

                            # Save final response to memory
                            await self.memory.save_message(session_id, "assistant", final_response)
                    else:
                        # Save response to memory
                        await self.memory.save_message(session_id, "assistant", full_response)
                else:
                    # Save response to memory
                    await self.memory.save_message(session_id, "assistant", full_response)

        else:
            # Non-streaming response
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self.system_prompt,
                messages=messages,
                tools=self.tools,
            )

            # Process tool calls if any
            if response.stop_reason == "tool_use":
                tool_results = []
                for content_block in response.content:
                    if content_block.type == 'tool_use':
                        tool_result = await self.process_tool_call(
                            content_block.name,
                            content_block.input
                        )
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": content_block.id,
                            "content": json.dumps(tool_result)
                        })

                if tool_results:
                    messages.append({
                        "role": "assistant",
                        "content": response.content
                    })
                    messages.append({
                        "role": "user",
                        "content": tool_results
                    })

                    # Make final call with tool results
                    final_response = await self.client.messages.create(
                        model=self.model,
                        max_tokens=self.max_tokens,
                        temperature=self.temperature,
                        system=self.system_prompt,
                        messages=messages,
                    )

                    response_text = ""
                    for block in final_response.content:
                        if hasattr(block, 'text'):
                            response_text += block.text

                    await self.memory.save_message(session_id, "assistant", response_text)
                    yield response_text
            else:
                # Extract text from response
                response_text = ""
                for block in response.content:
                    if hasattr(block, 'text'):
                        response_text += block.text

                await self.memory.save_message(session_id, "assistant", response_text)
                yield response_text

    async def get_welcome_message(self) -> str:
        """Get welcome message for new sessions"""
        return self.agent_config.get('welcome_message', 'Hello! How can I help you today?')

    async def clear_session(self, session_id: str):
        """Clear a chat session"""
        await self.memory.clear_history(session_id)

    async def close(self):
        """Cleanup resources"""
        await self.memory.disconnect()

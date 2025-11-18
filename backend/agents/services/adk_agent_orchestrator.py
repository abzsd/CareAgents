import asyncio
from typing import Optional, Dict, Any, AsyncGenerator
from enum import Enum

from ..adk_chat_agent import AdkChatAgent
from ..adk_record_agent import AdkRecordAgent
from ..adk_tools import PostgresConfig, init_postgres_toolkit
from .streaming_service import StreamingService, MessageType


class AgentType(str, Enum):
    """Available agent types"""
    CHAT = "chat"
    RECORD = "record"


class AdkAgentOrchestrator:
    """
    Orchestrates multiple AI agents (ADK-based) and manages their lifecycle
    Routes requests to appropriate agents and handles streaming responses
    """

    def __init__(
        self,
        google_api_key: str,
        postgres_config: PostgresConfig,
        redis_url: str = "redis://localhost:6379",
        streaming_service: Optional[StreamingService] = None
    ):
        self.google_api_key = google_api_key
        self.postgres_config = postgres_config
        self.redis_url = redis_url
        self.streaming_service = streaming_service

        # Initialize PostgreSQL toolkit (using adk_tools)
        init_postgres_toolkit(postgres_config)

        # Agent instances
        self.chat_agent: Optional[AdkChatAgent] = None
        self.record_agent: Optional[AdkRecordAgent] = None

        # Agent initialization lock
        self._init_lock = asyncio.Lock()

    async def _ensure_chat_agent(self) -> AdkChatAgent:
        """Lazy initialization of chat agent"""
        if self.chat_agent is None:
            async with self._init_lock:
                if self.chat_agent is None:
                    self.chat_agent = AdkChatAgent(
                        redis_url=self.redis_url
                    )
        return self.chat_agent

    async def _ensure_record_agent(self) -> AdkRecordAgent:
        """Lazy initialization of record agent"""
        if self.record_agent is None:
            async with self._init_lock:
                if self.record_agent is None:
                    self.record_agent = AdkRecordAgent(
                        temperature=0.1
                    )
        return self.record_agent

    async def process_chat_message(
        self,
        message: str,
        session_id: str,
        patient_id: Optional[str] = None,
        stream: bool = True
    ) -> AsyncGenerator[str, None]:
        """
        Process a chat message through the AdkChatAgent
        """
        agent = await self._ensure_chat_agent()

        if self.streaming_service and stream:
            await self.streaming_service.send_typing(session_id, True)
            await self.streaming_service.send_stream_start(session_id, AgentType.CHAT)

        try:
            async for chunk in agent.chat(
                message=message,
                session_id=session_id,
                patient_id=patient_id,
                stream=stream
            ):
                if self.streaming_service and stream:
                    await self.streaming_service.send_stream_chunk(session_id, chunk)
                yield chunk

            if self.streaming_service and stream:
                await self.streaming_service.send_stream_end(session_id)
                await self.streaming_service.send_typing(session_id, False)

        except Exception as e:
            error_msg = f"Error processing chat message: {str(e)}"
            if self.streaming_service:
                await self.streaming_service.send_error(session_id, error_msg, "CHAT_ERROR")
            yield error_msg

    async def get_patient_summary(
        self,
        patient_id: str,
        session_id: str,
        stream: bool = True
    ) -> AsyncGenerator[str, None]:
        """
        Get patient record summary through AdkRecordAgent
        """
        agent = await self._ensure_record_agent()

        if self.streaming_service and stream:
            await self.streaming_service.send_typing(session_id, True)
            await self.streaming_service.send_stream_start(session_id, AgentType.RECORD)

        try:
            async for chunk in agent.get_patient_summary(
                patient_id=patient_id,
                stream=stream
            ):
                if self.streaming_service and stream:
                    await self.streaming_service.send_stream_chunk(session_id, chunk)
                yield chunk

            if self.streaming_service and stream:
                await self.streaming_service.send_stream_end(session_id)
                await self.streaming_service.send_typing(session_id, False)

        except Exception as e:
            error_msg = f"Error getting patient summary: {str(e)}"
            if self.streaming_service:
                await self.streaming_service.send_error(session_id, error_msg, "RECORD_ERROR")
            yield error_msg

    async def analyze_vitals(
        self,
        patient_id: str,
        session_id: str,
        vital_type: Optional[str] = None,
        days: int = 30,
        stream: bool = True
    ) -> AsyncGenerator[str, None]:
        """
        Analyze patient vitals through AdkRecordAgent
        """
        agent = await self._ensure_record_agent()

        if self.streaming_service and stream:
            await self.streaming_service.send_typing(session_id, True)
            await self.streaming_service.send_stream_start(session_id, AgentType.RECORD)

        try:
            async for chunk in agent.analyze_vitals(
                patient_id=patient_id,
                vital_type=vital_type,
                days=days,
                stream=stream
            ):
                if self.streaming_service and stream:
                    await self.streaming_service.send_stream_chunk(session_id, chunk)
                yield chunk

            if self.streaming_service and stream:
                await self.streaming_service.send_stream_end(session_id)
                await self.streaming_service.send_typing(session_id, False)

        except Exception as e:
            error_msg = f"Error analyzing vitals: {str(e)}"
            if self.streaming_service:
                await self.streaming_service.send_error(session_id, error_msg, "VITALS_ERROR")
            yield error_msg

    async def summarize_prescriptions(
        self,
        patient_id: str,
        session_id: str,
        stream: bool = True
    ) -> AsyncGenerator[str, None]:
        """
        Summarize patient prescriptions through AdkRecordAgent
        """
        agent = await self._ensure_record_agent()

        if self.streaming_service and stream:
            await self.streaming_service.send_typing(session_id, True)
            await self.streaming_service.send_stream_start(session_id, AgentType.RECORD)

        try:
            async for chunk in agent.summarize_prescriptions(
                patient_id=patient_id,
                stream=stream
            ):
                if self.streaming_service and stream:
                    await self.streaming_service.send_stream_chunk(session_id, chunk)
                yield chunk

            if self.streaming_service and stream:
                await self.streaming_service.send_stream_end(session_id)
                await self.streaming_service.send_typing(session_id, False)

        except Exception as e:
            error_msg = f"Error summarizing prescriptions: {str(e)}"
            if self.streaming_service:
                await self.streaming_service.send_error(session_id, error_msg, "PRESCRIPTION_ERROR")
            yield error_msg

    async def handle_user_query(
        self,
        query: str,
        session_id: str,
        patient_id: Optional[str] = None,
        stream: bool = True
    ) -> AsyncGenerator[str, None]:
        """
        Intelligent query routing - determines which agent to use based on query
        """
        query_lower = query.lower()

        record_keywords = [
            'record', 'medical history', 'health records', 'vitals',
            'prescription', 'medication', 'report', 'summary',
            'lab result', 'diagnosis', 'treatment'
        ]

        is_record_query = any(keyword in query_lower for keyword in record_keywords)

        if is_record_query and patient_id:
            if 'vital' in query_lower or 'blood pressure' in query_lower or 'heart rate' in query_lower:
                async for chunk in self.analyze_vitals(patient_id, session_id, stream=stream):
                    yield chunk
            elif 'prescription' in query_lower or 'medication' in query_lower:
                async for chunk in self.summarize_prescriptions(patient_id, session_id, stream=stream):
                    yield chunk
            elif 'summary' in query_lower or 'overview' in query_lower or 'complete record' in query_lower:
                async for chunk in self.get_patient_summary(patient_id, session_id, stream=stream):
                    yield chunk
            else:
                async for chunk in self.process_chat_message(query, session_id, patient_id, stream):
                    yield chunk
        else:
            async for chunk in self.process_chat_message(query, session_id, patient_id, stream):
                yield chunk

    async def get_welcome_message(self, session_id: str) -> str:
        """Get welcome message for a new session"""
        agent = await self._ensure_chat_agent()
        return await agent.get_welcome_message()

    async def clear_session(self, session_id: str):
        """Clear session data"""
        if self.chat_agent:
            await self.chat_agent.clear_session(session_id)

    async def cleanup(self):
        """Cleanup resources"""
        if self.chat_agent:
            await self.chat_agent.close()

        # Close PostgreSQL toolkit
        from ..adk_tools import get_postgres_toolkit
        toolkit = get_postgres_toolkit()
        await toolkit.close()


# Global orchestrator instance
_orchestrator: Optional[AdkAgentOrchestrator] = None


def init_orchestrator(
    google_api_key: str, 
    postgres_config: PostgresConfig,
    redis_url: str = "redis://localhost:6379",
    streaming_service: Optional[StreamingService] = None
) -> AdkAgentOrchestrator:
    """Initialize the global agent orchestrator"""
    global _orchestrator
    _orchestrator = AdkAgentOrchestrator(
        google_api_key=google_api_key,
        postgres_config=postgres_config,
        redis_url=redis_url,
        streaming_service=streaming_service
    )
    return _orchestrator


def get_orchestrator() -> AdkAgentOrchestrator:
    """Get the global agent orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        raise RuntimeError("AdkAgentOrchestrator not initialized. Call init_orchestrator first.")
    return _orchestrator

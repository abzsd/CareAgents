"""
Streaming Service - WebSocket-based message buffer for frontend communication
"""
import json
import asyncio
from typing import Dict, Set, Optional, Any
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from enum import Enum


class MessageType(str, Enum):
    """Message types for WebSocket communication"""
    CONNECTED = "connected"
    CHAT_MESSAGE = "chat_message"
    CHAT_RESPONSE = "chat_response"
    STREAM_START = "stream_start"
    STREAM_CHUNK = "stream_chunk"
    STREAM_END = "stream_end"
    ERROR = "error"
    RECORD_REQUEST = "record_request"
    RECORD_RESPONSE = "record_response"
    SYSTEM = "system"
    TYPING = "typing"


class ConnectionManager:
    """Manages WebSocket connections"""

    def __init__(self):
        # Active connections: session_id -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}
        # User to session mapping: user_id -> session_id
        self.user_sessions: Dict[str, str] = {}

    async def connect(self, websocket: WebSocket, session_id: str, user_id: Optional[str] = None):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections[session_id] = websocket

        if user_id:
            self.user_sessions[user_id] = session_id

        # Send connection confirmation
        await self.send_message(session_id, {
            "type": MessageType.CONNECTED,
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Connected to CareAgents AI"
        })

    def disconnect(self, session_id: str, user_id: Optional[str] = None):
        """Remove a WebSocket connection"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]

        if user_id and user_id in self.user_sessions:
            del self.user_sessions[user_id]

    async def send_message(self, session_id: str, message: Dict[str, Any]):
        """Send a message to a specific session"""
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            try:
                await websocket.send_json(message)
            except Exception as e:
                print(f"Error sending message to {session_id}: {e}")
                # Connection might be broken, remove it
                self.disconnect(session_id)

    async def send_stream_chunk(self, session_id: str, chunk: str, metadata: Optional[Dict] = None):
        """Send a streaming chunk to a session"""
        message = {
            "type": MessageType.STREAM_CHUNK,
            "chunk": chunk,
            "timestamp": datetime.utcnow().isoformat()
        }
        if metadata:
            message["metadata"] = metadata

        await self.send_message(session_id, message)

    async def send_error(self, session_id: str, error: str, code: Optional[str] = None):
        """Send an error message to a session"""
        await self.send_message(session_id, {
            "type": MessageType.ERROR,
            "error": error,
            "code": code,
            "timestamp": datetime.utcnow().isoformat()
        })

    async def send_typing_indicator(self, session_id: str, is_typing: bool):
        """Send typing indicator"""
        await self.send_message(session_id, {
            "type": MessageType.TYPING,
            "is_typing": is_typing,
            "timestamp": datetime.utcnow().isoformat()
        })

    def is_connected(self, session_id: str) -> bool:
        """Check if a session is connected"""
        return session_id in self.active_connections

    async def broadcast(self, message: Dict[str, Any], exclude: Optional[Set[str]] = None):
        """Broadcast a message to all connected sessions"""
        exclude = exclude or set()
        for session_id in list(self.active_connections.keys()):
            if session_id not in exclude:
                await self.send_message(session_id, message)


class StreamingService:
    """
    WebSocket-based streaming service for agent communication
    Acts as a message buffer between backend agents and frontend
    """

    def __init__(self):
        self.connection_manager = ConnectionManager()
        self.message_queue: Dict[str, asyncio.Queue] = {}

    async def handle_websocket(self, websocket: WebSocket, session_id: str, user_id: Optional[str] = None):
        """
        Handle a WebSocket connection lifecycle

        Args:
            websocket: The WebSocket connection
            session_id: Unique session identifier
            user_id: Optional user identifier
        """
        await self.connection_manager.connect(websocket, session_id, user_id)

        # Create message queue for this session
        if session_id not in self.message_queue:
            self.message_queue[session_id] = asyncio.Queue()

        try:
            while True:
                # Receive messages from the client
                data = await websocket.receive_json()

                # Process the message
                await self.process_message(session_id, data)

        except WebSocketDisconnect:
            self.connection_manager.disconnect(session_id, user_id)
            if session_id in self.message_queue:
                del self.message_queue[session_id]
        except Exception as e:
            print(f"WebSocket error for session {session_id}: {e}")
            await self.connection_manager.send_error(
                session_id,
                f"Connection error: {str(e)}",
                "WEBSOCKET_ERROR"
            )
            self.connection_manager.disconnect(session_id, user_id)
            if session_id in self.message_queue:
                del self.message_queue[session_id]

    async def process_message(self, session_id: str, data: Dict[str, Any]):
        """
        Process an incoming message from the client

        Args:
            session_id: The session identifier
            data: The message data
        """
        message_type = data.get("type")

        if message_type == MessageType.CHAT_MESSAGE:
            # Queue the message for processing by the agent orchestrator
            if session_id in self.message_queue:
                await self.message_queue[session_id].put(data)

        elif message_type == MessageType.RECORD_REQUEST:
            # Queue record request
            if session_id in self.message_queue:
                await self.message_queue[session_id].put(data)

        else:
            # Unknown message type
            await self.connection_manager.send_error(
                session_id,
                f"Unknown message type: {message_type}",
                "INVALID_MESSAGE_TYPE"
            )

    async def get_message(self, session_id: str, timeout: float = 30.0) -> Optional[Dict[str, Any]]:
        """
        Get the next message from the session queue

        Args:
            session_id: The session identifier
            timeout: Timeout in seconds

        Returns:
            The message data or None if timeout
        """
        if session_id not in self.message_queue:
            return None

        try:
            message = await asyncio.wait_for(
                self.message_queue[session_id].get(),
                timeout=timeout
            )
            return message
        except asyncio.TimeoutError:
            return None

    async def send_chat_response(self, session_id: str, response: str, metadata: Optional[Dict] = None):
        """Send a complete chat response"""
        message = {
            "type": MessageType.CHAT_RESPONSE,
            "response": response,
            "timestamp": datetime.utcnow().isoformat()
        }
        if metadata:
            message["metadata"] = metadata

        await self.connection_manager.send_message(session_id, message)

    async def send_stream_start(self, session_id: str, agent_type: str):
        """Signal the start of a streaming response"""
        await self.connection_manager.send_message(session_id, {
            "type": MessageType.STREAM_START,
            "agent_type": agent_type,
            "timestamp": datetime.utcnow().isoformat()
        })

    async def send_stream_chunk(self, session_id: str, chunk: str, metadata: Optional[Dict] = None):
        """Send a streaming chunk"""
        await self.connection_manager.send_stream_chunk(session_id, chunk, metadata)

    async def send_stream_end(self, session_id: str, metadata: Optional[Dict] = None):
        """Signal the end of a streaming response"""
        message = {
            "type": MessageType.STREAM_END,
            "timestamp": datetime.utcnow().isoformat()
        }
        if metadata:
            message["metadata"] = metadata

        await self.connection_manager.send_message(session_id, message)

    async def send_error(self, session_id: str, error: str, code: Optional[str] = None):
        """Send an error message"""
        await self.connection_manager.send_error(session_id, error, code)

    async def send_typing(self, session_id: str, is_typing: bool):
        """Send typing indicator"""
        await self.connection_manager.send_typing_indicator(session_id, is_typing)

    def is_connected(self, session_id: str) -> bool:
        """Check if a session is connected"""
        return self.connection_manager.is_connected(session_id)

    async def broadcast_system_message(self, message: str):
        """Broadcast a system message to all connected sessions"""
        await self.connection_manager.broadcast({
            "type": MessageType.SYSTEM,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        })


# Global streaming service instance
_streaming_service: Optional[StreamingService] = None


def get_streaming_service() -> StreamingService:
    """Get the global streaming service instance"""
    global _streaming_service
    if _streaming_service is None:
        _streaming_service = StreamingService()
    return _streaming_service

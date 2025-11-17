"""
CareAgents Backend - Main application with AI Agents and WebSocket support
"""
import os
import uuid
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from agents.services.streaming_service import get_streaming_service, StreamingService, MessageType
from agents.services.adk_agent_orchestrator import init_orchestrator, get_orchestrator, AdkAgentOrchestrator
from agents.adk_tools import PostgresConfig

# Load environment variables
load_dotenv()


# Lifespan context manager for startup and shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("🚀 Starting CareAgents AI Backend...")

    # Initialize PostgreSQL configuration
    postgres_config = PostgresConfig(
        host=os.getenv("POSTGRES_HOST", os.getenv("DB_HOST", "localhost")),
        port=int(os.getenv("POSTGRES_PORT", os.getenv("DB_PORT", "5432"))),
        database=os.getenv("POSTGRES_DB", os.getenv("DB_NAME", "careagents")),
        user=os.getenv("POSTGRES_USER", os.getenv("DB_USER", "postgres")),
        password=os.getenv("POSTGRES_PASSWORD", os.getenv("DB_PASSWORD", "postgres")),
        ssl=os.getenv("POSTGRES_SSL", os.getenv("DB_SSL")),
        timeout=float(os.getenv("POSTGRES_TIMEOUT", os.getenv("DB_TIMEOUT", "60"))),
        command_timeout=float(os.getenv("POSTGRES_COMMAND_TIMEOUT", os.getenv("DB_COMMAND_TIMEOUT", "60"))),
    )

    # Get streaming service
    streaming_service = get_streaming_service()

    # Initialize agent orchestrator
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is required")

    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

    orchestrator = init_orchestrator(
        google_api_key=google_api_key,
        postgres_config=postgres_config,
        redis_url=redis_url,
        streaming_service=streaming_service
    )

    print("✅ Agent orchestrator initialized")
    print("✅ WebSocket streaming service ready")

    yield

    # Shutdown
    print("🔄 Shutting down CareAgents AI Backend...")
    await orchestrator.cleanup()
    print("✅ Cleanup complete")


# Create FastAPI app
app = FastAPI(
    title="CareAgents AI Backend",
    description="Healthcare Management System with AI Agents",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React/Vite default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class ChatRequest(BaseModel):
    message: str
    patient_id: Optional[str] = None
    session_id: Optional[str] = None


class RecordRequest(BaseModel):
    patient_id: str
    request_type: str  # 'summary', 'vitals', 'prescriptions'
    session_id: Optional[str] = None
    vital_type: Optional[str] = None
    days: int = 30


class ChatResponse(BaseModel):
    response: str
    session_id: str


# Dependency to get orchestrator
def get_agent_orchestrator() -> AdkAgentOrchestrator:
    return get_orchestrator()


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "CareAgents AI Backend",
        "version": "1.0.0"
    }


# WebSocket endpoint for real-time agent communication
@app.websocket("/ws/agent/{session_id}")
async def websocket_agent_endpoint(
    websocket: WebSocket,
    session_id: str,
    user_id: Optional[str] = None
):
    """
    WebSocket endpoint for real-time AI agent communication

    Args:
        websocket: WebSocket connection
        session_id: Unique session identifier
        user_id: Optional user identifier for tracking
    """
    streaming_service = get_streaming_service()
    orchestrator = get_orchestrator()

    # Handle the WebSocket connection
    await streaming_service.handle_websocket(websocket, session_id, user_id)


# Background task processor for WebSocket messages
@app.websocket("/ws/chat/{session_id}")
async def websocket_chat_endpoint(
    websocket: WebSocket,
    session_id: str,
    patient_id: Optional[str] = None
):
    """
    WebSocket endpoint specifically for chat interactions

    Args:
        websocket: WebSocket connection
        session_id: Session identifier
        patient_id: Optional patient ID for context
    """
    streaming_service = get_streaming_service()
    orchestrator = get_orchestrator()

    await websocket.accept()

    # Send welcome message
    welcome_msg = await orchestrator.get_welcome_message(session_id)
    await websocket.send_json({
        "type": MessageType.CONNECTED,
        "session_id": session_id,
        "message": welcome_msg
    })

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()

            message_type = data.get("type")
            message_content = data.get("message", "")

            if message_type == MessageType.CHAT_MESSAGE:
                # Process chat message with streaming
                await streaming_service.send_stream_start(session_id, "chat")

                full_response = ""
                async for chunk in orchestrator.process_chat_message(
                    message=message_content,
                    session_id=session_id,
                    patient_id=patient_id or data.get("patient_id"),
                    stream=True
                ):
                    full_response += chunk
                    await websocket.send_json({
                        "type": MessageType.STREAM_CHUNK,
                        "chunk": chunk
                    })

                await websocket.send_json({
                    "type": MessageType.STREAM_END,
                    "full_response": full_response
                })

    except WebSocketDisconnect:
        print(f"WebSocket disconnected for session: {session_id}")
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.send_json({
            "type": MessageType.ERROR,
            "error": str(e)
        })


# REST API endpoints (for non-streaming requests)

@app.post("/api/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator)
):
    """
    Non-streaming chat endpoint

    Args:
        request: Chat request with message and optional context

    Returns:
        Complete chat response
    """
    session_id = request.session_id or str(uuid.uuid4())

    full_response = ""
    async for chunk in orchestrator.process_chat_message(
        message=request.message,
        session_id=session_id,
        patient_id=request.patient_id,
        stream=False
    ):
        full_response += chunk

    return ChatResponse(
        response=full_response,
        session_id=session_id
    )


@app.post("/api/records/summary")
async def get_patient_summary(
    request: RecordRequest,
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator)
):
    """
    Get patient record summary

    Args:
        request: Record request with patient_id

    Returns:
        Patient summary
    """
    session_id = request.session_id or str(uuid.uuid4())

    full_response = ""
    async for chunk in orchestrator.get_patient_summary(
        patient_id=request.patient_id,
        session_id=session_id,
        stream=False
    ):
        full_response += chunk

    return {
        "summary": full_response,
        "patient_id": request.patient_id,
        "session_id": session_id
    }


@app.post("/api/records/vitals")
async def analyze_vitals(
    request: RecordRequest,
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator)
):
    """
    Analyze patient vitals

    Args:
        request: Record request with patient_id and optional filters

    Returns:
        Vitals analysis
    """
    session_id = request.session_id or str(uuid.uuid4())

    full_response = ""
    async for chunk in orchestrator.analyze_vitals(
        patient_id=request.patient_id,
        session_id=session_id,
        vital_type=request.vital_type,
        days=request.days,
        stream=False
    ):
        full_response += chunk

    return {
        "analysis": full_response,
        "patient_id": request.patient_id,
        "session_id": session_id
    }


@app.post("/api/records/prescriptions")
async def summarize_prescriptions(
    request: RecordRequest,
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator)
):
    """
    Summarize patient prescriptions

    Args:
        request: Record request with patient_id

    Returns:
        Prescription summary
    """
    session_id = request.session_id or str(uuid.uuid4())

    full_response = ""
    async for chunk in orchestrator.summarize_prescriptions(
        patient_id=request.patient_id,
        session_id=session_id,
        stream=False
    ):
        full_response += chunk

    return {
        "summary": full_response,
        "patient_id": request.patient_id,
        "session_id": session_id
    }


@app.delete("/api/session/{session_id}")
async def clear_session(
    session_id: str,
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator)
):
    """
    Clear a chat session

    Args:
        session_id: Session identifier to clear

    Returns:
        Success message
    """
    await orchestrator.clear_session(session_id)
    return {
        "message": "Session cleared successfully",
        "session_id": session_id
    }


# Run the application
if __name__ == "__main__":
    import uvicorn

    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    reload = os.getenv("API_RELOAD", "true").lower() == "true"

    uvicorn.run(
        "main_agents:app",
        host=host,
        port=port,
        reload=reload
    )

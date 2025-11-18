"""
Voice Chat WebSocket Route
Integrates with Gemini Live API for real-time voice interaction
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from google import genai
from google.genai import types
import asyncio
import json
import os
import logging
import base64

logger = logging.getLogger(__name__)
router = APIRouter()

# Model configuration
MODEL = "gemini-live-2.5-flash-preview"

def get_gemini_client():
    """Get Gemini client with API key validation"""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables")
    return genai.Client(api_key=api_key)


class VoiceChatSession:
    """Manages a single voice chat session with Gemini Live API"""

    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.gemini_session = None
        self.is_active = False
        self.send_task = None
        self.receive_task = None

    async def start(self):
        """Start the voice chat session"""
        try:
            # Get Gemini client
            client = get_gemini_client()

            # Configure Gemini Live API for audio input/output
            config = {
                "response_modalities": ["AUDIO"],
                "speech_config": {
                    "voice_config": {
                        "prebuilt_voice_config": {
                            "voice_name": "Aoede"  # You can change this to other voices
                        }
                    }
                }
            }

            # Connect to Gemini Live API
            self.gemini_session = client.aio.live.connect(model=MODEL, config=config)
            session = await self.gemini_session.__aenter__()
            self.is_active = True

            logger.info("Voice chat session started")

            # Send initial success message to client
            await self.websocket.send_json({
                "type": "session_started",
                "message": "Voice chat session connected"
            })

            # Create tasks for bidirectional communication
            self.receive_task = asyncio.create_task(self.receive_from_gemini(session))
            self.send_task = asyncio.create_task(self.receive_from_client(session))

            # Wait for either task to complete
            await asyncio.gather(self.receive_task, self.send_task, return_exceptions=True)

        except Exception as e:
            logger.error(f"Error starting voice chat session: {e}")
            await self.websocket.send_json({
                "type": "error",
                "message": str(e)
            })
        finally:
            await self.stop()

    async def receive_from_client(self, session):
        """Receive audio data from the client and send to Gemini"""
        try:
            while self.is_active:
                # Receive message from client
                message = await self.websocket.receive()

                if "text" in message:
                    data = json.loads(message["text"])

                    if data.get("type") == "audio_data":
                        # Client sent audio data (base64 encoded)
                        audio_bytes = base64.b64decode(data["audio"])

                        # Send audio to Gemini Live API
                        await session.send_client_content(
                            turns={
                                "role": "user",
                                "parts": [{
                                    "inline_data": {
                                        "mime_type": "audio/pcm",
                                        "data": audio_bytes
                                    }
                                }]
                            },
                            turn_complete=False  # Streaming mode
                        )

                    elif data.get("type") == "audio_end":
                        # Client finished speaking, mark turn complete
                        await session.send_client_content(
                            turns={"role": "user", "parts": []},
                            turn_complete=True
                        )
                        logger.info("Client finished speaking, requesting response")

                    elif data.get("type") == "text_message":
                        # Client sent text message
                        text = data.get("text", "")
                        await session.send_client_content(
                            turns={
                                "role": "user",
                                "parts": [{"text": text}]
                            },
                            turn_complete=True
                        )
                        logger.info(f"Client sent text: {text}")

                    elif data.get("type") == "stop":
                        # Client wants to stop
                        self.is_active = False
                        break

        except WebSocketDisconnect:
            logger.info("Client disconnected")
            self.is_active = False
        except Exception as e:
            logger.error(f"Error receiving from client: {e}")
            self.is_active = False

    async def receive_from_gemini(self, session):
        """Receive responses from Gemini and send to client"""
        try:
            while self.is_active:
                # Receive from Gemini Live API
                turn = session.receive()

                async for response in turn:
                    if response.data is not None:
                        # Gemini sent audio data
                        audio_base64 = base64.b64encode(response.data).decode('utf-8')

                        await self.websocket.send_json({
                            "type": "audio_response",
                            "audio": audio_base64,
                            "mime_type": "audio/pcm"
                        })

                    elif response.text is not None:
                        # Gemini sent text data
                        await self.websocket.send_json({
                            "type": "text_response",
                            "text": response.text
                        })

                    # Check if turn is complete
                    if response.server_content and response.server_content.turn_complete:
                        await self.websocket.send_json({
                            "type": "turn_complete"
                        })
                        logger.info("Gemini finished responding")

        except Exception as e:
            logger.error(f"Error receiving from Gemini: {e}")
            self.is_active = False

    async def stop(self):
        """Stop the voice chat session"""
        self.is_active = False

        # Cancel tasks
        if self.send_task and not self.send_task.done():
            self.send_task.cancel()
        if self.receive_task and not self.receive_task.done():
            self.receive_task.cancel()

        # Close Gemini session
        if self.gemini_session:
            try:
                await self.gemini_session.__aexit__(None, None, None)
                logger.info("Gemini session closed")
            except Exception as e:
                logger.error(f"Error closing Gemini session: {e}")


@router.websocket("/ws/voice-chat")
async def voice_chat_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for voice chat with Gemini Live API

    Client sends:
    - {"type": "audio_data", "audio": "base64_encoded_audio"} - streaming audio chunks
    - {"type": "audio_end"} - when user stops speaking
    - {"type": "text_message", "text": "message"} - text message
    - {"type": "stop"} - to end the session

    Server sends:
    - {"type": "session_started", "message": "..."} - when session starts
    - {"type": "audio_response", "audio": "base64_encoded_audio", "mime_type": "audio/pcm"} - audio response
    - {"type": "text_response", "text": "..."} - text response
    - {"type": "turn_complete"} - when model finishes responding
    - {"type": "error", "message": "..."} - error messages
    """
    await websocket.accept()
    logger.info("WebSocket connection accepted")

    session = VoiceChatSession(websocket)

    try:
        await session.start()
    except WebSocketDisconnect:
        logger.info("Client disconnected from voice chat")
    except Exception as e:
        logger.error(f"Error in voice chat websocket: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })
        except:
            pass
    finally:
        await session.stop()
        try:
            await websocket.close()
        except:
            pass
        logger.info("Voice chat session ended")

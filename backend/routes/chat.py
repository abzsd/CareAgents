"""
Chat routes for guest and authenticated users
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import os
import uuid
from anthropic import AsyncAnthropic

router = APIRouter(tags=["chat"])


class ChatMessage(BaseModel):
    """Chat message model"""
    role: str
    content: str


class GuestChatRequest(BaseModel):
    """Guest chat request"""
    message: str
    history: List[ChatMessage] = []


class GuestChatResponse(BaseModel):
    """Guest chat response"""
    message: str
    session_id: str


class GuestChatAgent:
    """
    Simple chat agent for guest users without database dependencies
    """

    def __init__(self, api_key: str):
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20241022"
        self.temperature = 0.7
        self.max_tokens = 2048

        self.system_prompt = """You are CareAgent's helpful AI assistant. You help visitors learn about the CareAgent platform.

**About CareAgent:**
- CareAgent is a comprehensive healthcare management platform
- We connect patients with certified healthcare professionals
- Features include: telemedicine consultations, health record management, prescription tracking, appointment scheduling, and AI-powered health insights
- We have 100+ healthcare professionals across various specializations
- Secure, HIPAA-compliant platform with enterprise-grade security
- 24/7 AI support for health queries
- Over 500 active patients and 10,000+ consultations completed
- 98% patient satisfaction rate

**Your role:**
1. Answer questions about CareAgent's features and services
2. Encourage users to sign up to access full features
3. Provide general healthcare information (but remind users you're not a doctor)
4. Be friendly, professional, and helpful
5. Never provide medical diagnoses or treatment advice
6. For emergencies, always direct users to call 911 or visit an emergency room

**Important guidelines:**
- You cannot book appointments or access patient data for guest users
- For full features, users must sign in with their Google account
- Keep responses concise and helpful
- Focus on the platform's benefits and features
- Be encouraging about signing up

If asked about pricing, services, doctors, appointments, or features - provide helpful information and encourage them to sign up for full access."""

    async def chat(self, message: str, history: List[Dict[str, str]]) -> str:
        """
        Process a guest chat message

        Args:
            message: User's message
            history: Conversation history

        Returns:
            Assistant's response
        """
        # Build messages
        messages = []

        # Add history (limit to last 10 messages to control costs)
        for msg in history[-10:]:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        # Add current message
        messages.append({
            "role": "user",
            "content": message
        })

        try:
            # Make API call
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self.system_prompt,
                messages=messages,
            )

            # Extract text from response
            response_text = ""
            for block in response.content:
                if hasattr(block, 'text'):
                    response_text += block.text

            return response_text.strip()

        except Exception as e:
            print(f"Error in guest chat: {str(e)}")
            return "I apologize, but I'm having trouble processing your request right now. Please try again in a moment, or sign in for full support."


# Initialize guest chat agent
_guest_agent: Optional[GuestChatAgent] = None


def get_guest_agent() -> GuestChatAgent:
    """Get or create guest chat agent"""
    global _guest_agent
    if _guest_agent is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=500,
                detail="ANTHROPIC_API_KEY not configured"
            )
        _guest_agent = GuestChatAgent(api_key=api_key)
    return _guest_agent


@router.post("/chat/guest", response_model=GuestChatResponse)
async def guest_chat(
    request: GuestChatRequest,
    agent: GuestChatAgent = Depends(get_guest_agent)
):
    """
    Guest chat endpoint for non-authenticated users

    This endpoint allows visitors to chat with an AI assistant
    to learn about CareAgent features and services.
    """
    try:
        # Convert history to dict format
        history = [{"role": msg.role, "content": msg.content} for msg in request.history]

        # Get response from agent
        response = await agent.chat(request.message, history)

        # Generate a session ID (in a real app, you might want to track this)
        session_id = str(uuid.uuid4())

        return GuestChatResponse(
            message=response,
            session_id=session_id
        )

    except Exception as e:
        print(f"Error in guest_chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to process chat message"
        )


@router.get("/chat/health")
async def chat_health():
    """Health check for chat service"""
    try:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            return {
                "status": "unhealthy",
                "error": "ANTHROPIC_API_KEY not configured"
            }

        return {
            "status": "healthy",
            "service": "Guest Chat",
            "model": "claude-3-5-sonnet-20241022"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

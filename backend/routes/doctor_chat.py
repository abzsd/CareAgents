"""
FastAPI routes for Doctor Chat Agent operations
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import os
import asyncpg

from agents.doctor_chat_agent import DoctorChatAgent
from database.postgresql.connection import get_postgresql_pool
from services.medical_history_service import MedicalHistoryService
from services.patient_service import PatientService

router = APIRouter(prefix="/doctor-chat", tags=["doctor-chat"])


class ChatRequest(BaseModel):
    query: str
    patient_id: str
    conversation_history: Optional[List[Dict[str, str]]] = None


class SummaryRequest(BaseModel):
    patient_id: str
    summary_type: str = "comprehensive"  # comprehensive, brief, recent, medications


class RiskAnalysisRequest(BaseModel):
    patient_id: str


def get_doctor_chat_agent() -> DoctorChatAgent:
    """Dependency to get doctor chat agent"""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google API key not configured"
        )
    return DoctorChatAgent(api_key)


async def get_patient_data(
    patient_id: str,
    pool: asyncpg.Pool = Depends(get_postgresql_pool)
) -> Dict[str, Any]:
    """
    Get complete patient data including demographics and medical history.

    Args:
        patient_id: Patient ID
        pool: Database connection pool

    Returns:
        Dictionary with patient_data and medical_history
    """
    patient_service = PatientService(pool)
    medical_history_service = MedicalHistoryService(pool)

    # Get patient demographics
    patient = await patient_service.get_patient(patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found"
        )

    # Get medical history
    history_result = await medical_history_service.get_patient_medical_history(
        patient_id,
        page=1,
        page_size=100  # Get all history for context
    )

    return {
        "patient_data": patient.model_dump(),
        "medical_history": history_result["records"]
    }


@router.post("/chat", status_code=status.HTTP_200_OK)
async def chat_with_doctor_agent(
    request: ChatRequest,
    agent: DoctorChatAgent = Depends(get_doctor_chat_agent),
    pool: asyncpg.Pool = Depends(get_postgresql_pool)
):
    """
    Chat with the doctor AI agent about a patient.

    Args:
        request: Chat request with query and patient ID

    Returns:
        AI-generated response
    """
    try:
        # Get patient data
        data = await get_patient_data(request.patient_id, pool)

        # Get AI response
        response = await agent.chat(
            query=request.query,
            patient_data=data["patient_data"],
            medical_history=data["medical_history"],
            conversation_history=request.conversation_history
        )

        return {
            "response": response,
            "patient_id": request.patient_id
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat failed: {str(e)}"
        )


@router.post("/chat/stream")
async def chat_with_streaming(
    request: ChatRequest,
    agent: DoctorChatAgent = Depends(get_doctor_chat_agent),
    pool: asyncpg.Pool = Depends(get_postgresql_pool)
):
    """
    Chat with streaming responses.

    Args:
        request: Chat request

    Returns:
        Streaming response
    """
    try:
        # Get patient data
        data = await get_patient_data(request.patient_id, pool)

        async def generate():
            async for chunk in agent.chat_stream(
                query=request.query,
                patient_data=data["patient_data"],
                medical_history=data["medical_history"],
                conversation_history=request.conversation_history
            ):
                yield chunk

        return StreamingResponse(
            generate(),
            media_type="text/plain"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Streaming chat failed: {str(e)}"
        )


@router.post("/summary", status_code=status.HTTP_200_OK)
async def get_patient_summary(
    request: SummaryRequest,
    agent: DoctorChatAgent = Depends(get_doctor_chat_agent),
    pool: asyncpg.Pool = Depends(get_postgresql_pool)
):
    """
    Get AI-generated patient summary.

    Args:
        request: Summary request with patient ID and type

    Returns:
        Patient summary
    """
    try:
        # Get patient data
        data = await get_patient_data(request.patient_id, pool)

        # Get summary
        summary = await agent.get_patient_summary(
            patient_data=data["patient_data"],
            medical_history=data["medical_history"],
            summary_type=request.summary_type
        )

        return {
            "summary": summary,
            "summary_type": request.summary_type,
            "patient_id": request.patient_id
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Summary generation failed: {str(e)}"
        )


@router.post("/risk-analysis", status_code=status.HTTP_200_OK)
async def analyze_patient_risk(
    request: RiskAnalysisRequest,
    agent: DoctorChatAgent = Depends(get_doctor_chat_agent),
    pool: asyncpg.Pool = Depends(get_postgresql_pool)
):
    """
    Analyze patient risk factors and health trends.

    Args:
        request: Risk analysis request

    Returns:
        Risk analysis with insights
    """
    try:
        # Get patient data
        data = await get_patient_data(request.patient_id, pool)

        # Analyze risk
        analysis = await agent.analyze_patient_risk(
            patient_data=data["patient_data"],
            medical_history=data["medical_history"]
        )

        return {
            **analysis,
            "patient_id": request.patient_id
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Risk analysis failed: {str(e)}"
        )

"""
AI-Powered Doctor Chat Agent using Google ADK
Provides intelligent patient summaries and answers to doctor queries
"""
import os
from typing import Dict, Any, List, Optional, AsyncGenerator
import json
import re
from datetime import datetime

from google import genai
from google.genai import types


class DoctorChatAgent:
    """
    AI Agent for doctor-patient interaction via chat.
    Provides intelligent summaries and answers based on patient data.
    """

    def __init__(self, api_key: str):
        """
        Initialize the doctor chat agent.

        Args:
            api_key: Google API key
        """
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-2.0-flash-exp"

    def _prepare_patient_context(
        self,
        patient_data: Dict[str, Any],
        medical_history: List[Dict[str, Any]]
    ) -> str:
        """
        Prepare patient context for the chat.

        Args:
            patient_data: Patient demographic and basic info
            medical_history: List of medical history records

        Returns:
            Formatted context string
        """
        context = f"""
PATIENT INFORMATION
==================
Name: {patient_data.get('first_name', '')} {patient_data.get('last_name', '')}
Age: {patient_data.get('age', 'N/A')} | Gender: {patient_data.get('gender', 'N/A')} | Blood Group: {patient_data.get('blood_group', 'N/A')}
Contact: {patient_data.get('phone', 'N/A')} | Email: {patient_data.get('email', 'N/A')}

ALLERGIES: {', '.join(patient_data.get('allergies', [])) if patient_data.get('allergies') else 'None reported'}
CHRONIC CONDITIONS: {', '.join(patient_data.get('chronic_conditions', [])) if patient_data.get('chronic_conditions') else 'None reported'}

MEDICAL HISTORY ({len(medical_history)} records)
==================
"""

        if medical_history:
            # Sort by date, most recent first
            sorted_history = sorted(
                medical_history,
                key=lambda x: x.get('visit_date', ''),
                reverse=True
            )

            for idx, record in enumerate(sorted_history, 1):
                context += f"\n{idx}. Visit on {record.get('visit_date', 'N/A')}\n"
                context += f"   Doctor: {record.get('doctor_name', 'N/A')}\n"
                context += f"   Diagnosis: {record.get('diagnosis', 'N/A')}\n"

                if record.get('symptoms'):
                    context += f"   Symptoms: {', '.join(record.get('symptoms', []))}\n"

                if record.get('prescriptions'):
                    context += "   Medications:\n"
                    for med in record.get('prescriptions', []):
                        context += f"     • {med.get('medication_name', 'N/A')}: {med.get('dosage', 'N/A')}, {med.get('frequency', 'N/A')}\n"

                if record.get('blood_pressure'):
                    context += f"   BP: {record.get('blood_pressure')} | "
                if record.get('heart_rate'):
                    context += f"HR: {record.get('heart_rate')} | "
                if record.get('temperature'):
                    context += f"Temp: {record.get('temperature')}"
                if any([record.get('blood_pressure'), record.get('heart_rate'), record.get('temperature')]):
                    context += "\n"

                if record.get('notes'):
                    context += f"   Notes: {record.get('notes')}\n"
        else:
            context += "No medical history available.\n"

        return context

    async def chat(
        self,
        query: str,
        patient_data: Dict[str, Any],
        medical_history: List[Dict[str, Any]],
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Process a doctor's query about a patient.

        Args:
            query: The doctor's question
            patient_data: Patient demographic and basic info
            medical_history: List of medical history records
            conversation_history: Previous conversation messages

        Returns:
            AI-generated response
        """
        try:
            # Prepare patient context
            patient_context = self._prepare_patient_context(patient_data, medical_history)

            # Build system instruction
            system_instruction = f"""You are an AI medical assistant helping a doctor review patient information.

You have access to the patient's complete medical records. Your role is to:
1. Provide accurate summaries of patient information
2. Identify patterns in medical history
3. Highlight important medical conditions, allergies, and chronic issues
4. Answer specific questions about the patient's history
5. Provide insights on medication history and treatment patterns

IMPORTANT:
- Only provide information based on the patient data provided
- Do not diagnose or provide treatment recommendations
- If information is not available in the records, clearly state that
- Use medical terminology appropriately
- Be concise and factual

PATIENT DATA:
{patient_context}
"""

            # Build conversation messages
            messages = []

            # Add conversation history if available
            if conversation_history:
                for msg in conversation_history:
                    messages.append(msg)

            # Add current query
            messages.append({"role": "user", "parts": [{"text": query}]})

            # Generate response
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=messages,
                config=types.GenerateContentConfig(
                    temperature=0.3,  # Low temperature for accuracy
                    system_instruction=system_instruction
                )
            )

            return response.text

        except Exception as e:
            print(f"Error in chat: {str(e)}")
            return f"I apologize, but I encountered an error processing your request: {str(e)}"

    async def get_patient_summary(
        self,
        patient_data: Dict[str, Any],
        medical_history: List[Dict[str, Any]],
        summary_type: str = "comprehensive"
    ) -> str:
        """
        Generate a patient summary.

        Args:
            patient_data: Patient demographic and basic info
            medical_history: List of medical history records
            summary_type: Type of summary - "comprehensive", "brief", "recent", "medications"

        Returns:
            Formatted summary
        """
        summary_prompts = {
            "comprehensive": "Provide a comprehensive summary of this patient's medical history, including all significant diagnoses, chronic conditions, current medications, and recent visits.",
            "brief": "Provide a brief 3-4 sentence summary of this patient's key medical information.",
            "recent": "Summarize only the most recent medical visits and current health status.",
            "medications": "List and summarize all medications this patient has been prescribed, noting any patterns or concerns.",
            "allergies_conditions": "Summarize the patient's allergies and chronic conditions, and their implications for treatment."
        }

        prompt = summary_prompts.get(summary_type, summary_prompts["comprehensive"])

        return await self.chat(
            query=prompt,
            patient_data=patient_data,
            medical_history=medical_history
        )

    async def chat_stream(
        self,
        query: str,
        patient_data: Dict[str, Any],
        medical_history: List[Dict[str, Any]],
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> AsyncGenerator[str, None]:
        """
        Process a doctor's query with streaming response.

        Args:
            query: The doctor's question
            patient_data: Patient demographic and basic info
            medical_history: List of medical history records
            conversation_history: Previous conversation messages

        Yields:
            Chunks of AI-generated response
        """
        try:
            # Prepare patient context
            patient_context = self._prepare_patient_context(patient_data, medical_history)

            # Build system instruction
            system_instruction = f"""You are an AI medical assistant helping a doctor review patient information.

You have access to the patient's complete medical records. Your role is to:
1. Provide accurate summaries of patient information
2. Identify patterns in medical history
3. Highlight important medical conditions, allergies, and chronic issues
4. Answer specific questions about the patient's history
5. Provide insights on medication history and treatment patterns

IMPORTANT:
- Only provide information based on the patient data provided
- Do not diagnose or provide treatment recommendations
- If information is not available in the records, clearly state that
- Use medical terminology appropriately
- Be concise and factual

PATIENT DATA:
{patient_context}
"""

            # Build conversation messages
            messages = []

            # Add conversation history if available
            if conversation_history:
                for msg in conversation_history:
                    messages.append(msg)

            # Add current query
            messages.append({"role": "user", "parts": [{"text": query}]})

            # Generate streaming response
            async for chunk in self.client.models.generate_content_stream(
                model=self.model_id,
                contents=messages,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    system_instruction=system_instruction
                )
            ):
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            print(f"Error in chat stream: {str(e)}")
            yield f"Error: {str(e)}"

    async def analyze_patient_risk(
        self,
        patient_data: Dict[str, Any],
        medical_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze patient risk factors and health trends.

        Args:
            patient_data: Patient demographic and basic info
            medical_history: List of medical history records

        Returns:
            Risk analysis with insights
        """
        prompt = """
Analyze this patient's medical history and identify:
1. Key risk factors (based on chronic conditions, age, lifestyle if mentioned)
2. Health trends (improving, stable, or declining)
3. Medication adherence patterns (if discernible)
4. Areas requiring attention or follow-up
5. Preventive care recommendations

Provide your analysis in JSON format:
{
    "risk_level": "low|moderate|high",
    "risk_factors": ["list of identified risk factors"],
    "health_trends": {
        "overall": "improving|stable|declining",
        "details": "brief explanation"
    },
    "areas_of_concern": ["list of areas needing attention"],
    "recommendations": ["list of preventive care or follow-up recommendations"],
    "summary": "brief overall assessment"
}
"""

        try:
            response = await self.chat(
                query=prompt,
                patient_data=patient_data,
                medical_history=medical_history
            )

            # Extract JSON from response (handle markdown code blocks)
            json_str = response.strip()

            # Check if response is wrapped in markdown code blocks
            if json_str.startswith('```'):
                # Extract content between code blocks
                match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', json_str, re.DOTALL)
                if match:
                    json_str = match.group(1).strip()

            # Try to parse as JSON
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                print(f"Response text: {json_str[:200]}")
                # If not valid JSON, return as text summary
                return {
                    "summary": response,
                    "risk_level": "unknown"
                }

        except Exception as e:
            print(f"Error analyzing patient risk: {str(e)}")
            return {
                "error": str(e),
                "risk_level": "unknown"
            }

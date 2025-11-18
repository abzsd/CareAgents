"""
AI-Powered Appointment Booking Agent using Google ADK
Intelligently matches patients with doctors and schedules appointments
"""
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, date, time, timedelta
import json

from google import genai
from google.genai import types

# Import database services
import asyncio
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class AppointmentBookingAgent:
    """
    AI Agent for intelligent appointment booking.
    Uses Google ADK to understand patient needs and match with appropriate doctors.
    """

    def __init__(self, api_key: str):
        """
        Initialize the appointment booking agent.

        Args:
            api_key: Google API key
        """
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-2.0-flash-exp"

    async def match_doctor(
        self,
        reason: str,
        symptoms: Optional[List[str]] = None,
        preferred_specialization: Optional[str] = None,
        available_doctors: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Use AI to match patient with the best doctor based on their needs.

        Args:
            reason: Reason for consultation
            symptoms: List of symptoms (optional)
            preferred_specialization: Preferred doctor specialization (optional)
            available_doctors: List of available doctors

        Returns:
            Dictionary with matched doctor and reasoning
        """
        # Prepare doctor information for the AI
        doctors_info = []
        for doc in available_doctors or []:
            doctors_info.append({
                "doctor_id": doc.get("doctor_id"),
                "name": f"Dr. {doc.get('first_name')} {doc.get('last_name')}",
                "specialization": doc.get("specialization"),
                "sub_specializations": doc.get("sub_specializations", []),
                "experience_years": doc.get("years_of_experience"),
                "rating": doc.get("rating"),
                "consultation_fee": doc.get("consultation_fee")
            })

        # Prepare the prompt
        symptoms_text = ", ".join(symptoms) if symptoms else "None specified"

        prompt = f"""
You are a medical appointment assistant. Based on the patient's needs, recommend the most suitable doctor.

Patient Information:
- Reason for consultation: {reason}
- Symptoms: {symptoms_text}
- Preferred specialization: {preferred_specialization or "None"}

Available Doctors:
{json.dumps(doctors_info, indent=2)}

Task:
1. Analyze the patient's needs and symptoms
2. Match them with the most appropriate doctor based on:
   - Specialization match
   - Sub-specializations
   - Experience
   - Rating
3. Provide a clear explanation for your recommendation

Respond in JSON format:
{{
    "recommended_doctor_id": "doctor_id",
    "doctor_name": "name",
    "specialization": "specialization",
    "confidence_score": 0-100,
    "reasoning": "explanation of why this doctor is recommended",
    "alternative_doctors": ["doctor_id1", "doctor_id2"]
}}
"""

        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    response_mime_type="application/json"
                )
            )

            result = json.loads(response.text)
            return result

        except Exception as e:
            print(f"Error in doctor matching: {str(e)}")
            # Fallback to rule-based matching
            return self._fallback_doctor_match(
                reason, symptoms, preferred_specialization, available_doctors
            )

    async def suggest_appointment_slots(
        self,
        doctor_availability: List[Dict[str, Any]],
        existing_appointments: List[Dict[str, Any]],
        patient_preference: Optional[str] = None,
        preferred_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Use AI to suggest optimal appointment slots.

        Args:
            doctor_availability: Doctor's available time slots
            existing_appointments: Doctor's existing appointments
            patient_preference: Patient's time preference (morning/afternoon/evening)
            preferred_date: Patient's preferred date

        Returns:
            Dictionary with suggested slots and reasoning
        """
        # Convert existing appointments to busy slots
        busy_slots = []
        for apt in existing_appointments:
            busy_slots.append({
                "date": str(apt.get("appointment_date")),
                "time": str(apt.get("appointment_time")),
                "duration": apt.get("duration_minutes", 30)
            })

        prompt = f"""
You are a medical appointment scheduling assistant. Based on the doctor's availability and existing appointments, suggest optimal time slots.

Doctor Availability:
{json.dumps(doctor_availability, indent=2)}

Existing Appointments (Busy Slots):
{json.dumps(busy_slots, indent=2)}

Patient Preferences:
- Preferred time of day: {patient_preference or "flexible"}
- Preferred date: {str(preferred_date) if preferred_date else "flexible"}

Task:
1. Consider doctor's availability schedule
2. Avoid conflicting with existing appointments
3. Consider patient's preferences
4. Suggest 3-5 optimal time slots over the next 7-14 days
5. Prioritize slots that match patient preferences

Respond in JSON format:
{{
    "suggested_slots": [
        {{
            "date": "YYYY-MM-DD",
            "time": "HH:MM:SS",
            "day_of_week": "Monday",
            "time_of_day": "morning/afternoon/evening",
            "confidence": 0-100
        }}
    ],
    "reasoning": "explanation of slot selection",
    "notes": "any additional notes or recommendations"
}}
"""

        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    response_mime_type="application/json"
                )
            )

            result = json.loads(response.text)
            return result

        except Exception as e:
            print(f"Error in slot suggestion: {str(e)}")
            # Fallback to simple slot generation
            return self._fallback_slot_generation(preferred_date)

    async def analyze_appointment_request(
        self,
        reason: str,
        symptoms: Optional[List[str]] = None,
        medical_history: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze the appointment request and extract key information.

        Args:
            reason: Reason for consultation
            symptoms: List of symptoms
            medical_history: Patient's medical history

        Returns:
            Dictionary with analysis results
        """
        symptoms_text = ", ".join(symptoms) if symptoms else "None specified"
        history_text = json.dumps(medical_history, indent=2) if medical_history else "No medical history available"

        prompt = f"""
You are a medical triage assistant. Analyze this appointment request and provide insights.

Appointment Request:
- Reason: {reason}
- Symptoms: {symptoms_text}

Medical History:
{history_text}

Task:
1. Determine the urgency level (routine, moderate, urgent, emergency)
2. Identify the most appropriate medical specialty
3. Suggest additional information that should be collected
4. Determine if teleconsultation is suitable

Respond in JSON format:
{{
    "urgency_level": "routine|moderate|urgent|emergency",
    "recommended_specialization": "specialization name",
    "alternative_specializations": ["spec1", "spec2"],
    "teleconsultation_suitable": true/false,
    "suggested_questions": ["question1", "question2"],
    "pre_appointment_notes": "any notes for the doctor",
    "reasoning": "explanation of the analysis"
}}
"""

        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    response_mime_type="application/json"
                )
            )

            result = json.loads(response.text)
            return result

        except Exception as e:
            print(f"Error in request analysis: {str(e)}")
            return {
                "urgency_level": "routine",
                "recommended_specialization": "General Practice",
                "alternative_specializations": [],
                "teleconsultation_suitable": True,
                "suggested_questions": [],
                "pre_appointment_notes": reason,
                "reasoning": "Unable to analyze - defaulting to general practice"
            }

    def _fallback_doctor_match(
        self,
        reason: str,
        symptoms: Optional[List[str]],
        preferred_specialization: Optional[str],
        available_doctors: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Fallback doctor matching using simple rules."""
        if not available_doctors:
            return {
                "recommended_doctor_id": None,
                "doctor_name": None,
                "specialization": None,
                "confidence_score": 0,
                "reasoning": "No doctors available",
                "alternative_doctors": []
            }

        # Simple rule-based matching
        matched_doctor = available_doctors[0]

        if preferred_specialization:
            for doc in available_doctors:
                if doc.get("specialization", "").lower() == preferred_specialization.lower():
                    matched_doctor = doc
                    break

        return {
            "recommended_doctor_id": matched_doctor.get("doctor_id"),
            "doctor_name": f"Dr. {matched_doctor.get('first_name')} {matched_doctor.get('last_name')}",
            "specialization": matched_doctor.get("specialization"),
            "confidence_score": 70,
            "reasoning": "Matched based on availability and specialization preference",
            "alternative_doctors": [doc.get("doctor_id") for doc in available_doctors[1:3]]
        }

    def _fallback_slot_generation(self, preferred_date: Optional[date] = None) -> Dict[str, Any]:
        """Fallback slot generation using simple rules."""
        slots = []
        start_date = preferred_date or date.today() + timedelta(days=1)

        # Generate slots for next 5 business days
        for i in range(5):
            current_date = start_date + timedelta(days=i)
            if current_date.weekday() < 5:  # Monday to Friday
                for hour in [9, 10, 14, 15, 16]:
                    slots.append({
                        "date": str(current_date),
                        "time": f"{hour:02d}:00:00",
                        "day_of_week": current_date.strftime("%A"),
                        "time_of_day": "morning" if hour < 12 else "afternoon",
                        "confidence": 80
                    })

        return {
            "suggested_slots": slots[:5],
            "reasoning": "Standard business hours slots",
            "notes": "These are default slots. Doctor will confirm availability."
        }

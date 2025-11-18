"""
AI-Powered Prescription Image Parser using Google ADK
Extracts prescription data from images and converts to structured format
"""
import os
from typing import Dict, Any, List, Optional
import json
import base64
from pathlib import Path

from google import genai
from google.genai import types


class PrescriptionParserAgent:
    """
    AI Agent for parsing prescription images.
    Uses Google ADK's vision capabilities to extract structured data.
    """

    def __init__(self, api_key: str):
        """
        Initialize the prescription parser agent.

        Args:
            api_key: Google API key
        """
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-2.0-flash-exp"

    async def parse_prescription_image(
        self,
        image_path: str = None,
        image_url: str = None,
        image_data: bytes = None
    ) -> Dict[str, Any]:
        """
        Parse a prescription image and extract structured data.

        Args:
            image_path: Path to local image file
            image_url: URL to image
            image_data: Raw image bytes

        Returns:
            Dictionary with structured prescription data
        """
        # Prepare image for API
        if image_path:
            with open(image_path, 'rb') as f:
                image_data = f.read()

        if not image_data and not image_url:
            raise ValueError("Either image_path, image_url, or image_data must be provided")

        prompt = """
You are a medical prescription parser. Analyze this prescription image and extract all relevant information.

Extract the following information:
1. Doctor Information:
   - Doctor name
   - Medical license number (if visible)
   - Clinic/Hospital name
   - Contact information

2. Patient Information:
   - Patient name
   - Age/Date of birth
   - Gender
   - Patient ID (if visible)

3. Prescription Date

4. Medications (for each medication extract):
   - Medication name (generic and brand name if both present)
   - Dosage/Strength
   - Frequency (how often to take)
   - Duration (how long to take)
   - Quantity/Number of pills
   - Special instructions (e.g., "take with food", "before bedtime")
   - Route of administration (oral, topical, etc.)

5. Diagnosis/Condition

6. Additional Notes/Instructions

7. Follow-up Information

8. Signature/Stamp details

IMPORTANT:
- Extract exactly what's written on the prescription
- If information is unclear or not visible, mark as "not_visible" or "unclear"
- Preserve medical terminology exactly as written
- Note any handwritten portions that are difficult to read

Respond in JSON format:
{
    "doctor": {
        "name": "string",
        "license": "string",
        "clinic": "string",
        "contact": "string"
    },
    "patient": {
        "name": "string",
        "age": "string",
        "gender": "string",
        "id": "string"
    },
    "date": "YYYY-MM-DD or as written",
    "medications": [
        {
            "name": "string",
            "brand_name": "string",
            "dosage": "string",
            "frequency": "string",
            "duration": "string",
            "quantity": "string",
            "instructions": "string",
            "route": "string"
        }
    ],
    "diagnosis": "string",
    "additional_notes": "string",
    "follow_up": "string",
    "confidence_score": 0-100,
    "unclear_portions": ["list of unclear parts"],
    "handwritten_sections": ["list of handwritten sections"],
    "warnings": ["any safety concerns or unclear critical information"]
}
"""

        try:
            # Create content with image
            if image_data:
                # Convert image to base64
                import mimetypes
                mime_type = "image/jpeg"  # Default
                if image_path:
                    mime_type = mimetypes.guess_type(image_path)[0] or "image/jpeg"

                # Upload the file first
                uploaded_file = self.client.files.upload(
                    path=image_path if image_path else None,
                    config=types.UploadFileConfig(
                        mime_type=mime_type,
                        display_name="prescription_image"
                    )
                )

                # Wait for file to be processed
                import time
                time.sleep(2)

                response = self.client.models.generate_content(
                    model=self.model_id,
                    contents=[
                        types.Part.from_uri(
                            file_uri=uploaded_file.uri,
                            mime_type=uploaded_file.mime_type
                        ),
                        prompt
                    ],
                    config=types.GenerateContentConfig(
                        temperature=0.1,  # Low temperature for accuracy
                        response_mime_type="application/json"
                    )
                )
            else:
                # Use URL
                response = self.client.models.generate_content(
                    model=self.model_id,
                    contents=[
                        types.Part.from_uri(
                            file_uri=image_url,
                            mime_type="image/jpeg"
                        ),
                        prompt
                    ],
                    config=types.GenerateContentConfig(
                        temperature=0.1,
                        response_mime_type="application/json"
                    )
                )

            result = json.loads(response.text)
            return result

        except Exception as e:
            print(f"Error parsing prescription: {str(e)}")
            return {
                "error": str(e),
                "doctor": {},
                "patient": {},
                "medications": [],
                "confidence_score": 0
            }

    async def validate_and_correct_prescription(
        self,
        extracted_data: Dict[str, Any],
        medical_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Validate extracted prescription data and suggest corrections.

        Args:
            extracted_data: Previously extracted prescription data
            medical_context: Additional medical context (patient history, allergies, etc.)

        Returns:
            Validated and corrected prescription data with warnings
        """
        context_text = json.dumps(medical_context, indent=2) if medical_context else "No additional context"

        prompt = f"""
You are a medical prescription validator. Review this extracted prescription data for:
1. Drug name spelling and accuracy
2. Dosage appropriateness
3. Drug interactions (if medical context provided)
4. Contraindications based on patient info
5. Completeness of information

Extracted Data:
{json.dumps(extracted_data, indent=2)}

Medical Context:
{context_text}

Respond in JSON format:
{{
    "is_valid": true/false,
    "corrections": [
        {{
            "field": "field_name",
            "original": "original_value",
            "suggested": "suggested_value",
            "reason": "explanation"
        }}
    ],
    "warnings": [
        {{
            "severity": "low|medium|high|critical",
            "category": "drug_interaction|dosage|allergy|contraindication|missing_info",
            "message": "detailed warning message",
            "recommendation": "what to do about it"
        }}
    ],
    "drug_interactions": ["list of potential interactions"],
    "missing_critical_info": ["list of missing important information"],
    "confidence_score": 0-100
}}
"""

        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    response_mime_type="application/json"
                )
            )

            result = json.loads(response.text)
            return result

        except Exception as e:
            print(f"Error validating prescription: {str(e)}")
            return {
                "is_valid": False,
                "error": str(e),
                "corrections": [],
                "warnings": [],
                "confidence_score": 0
            }

    async def convert_to_editable_format(
        self,
        prescription_data: Dict[str, Any]
    ) -> str:
        """
        Convert structured prescription data to human-readable, editable text format.

        Args:
            prescription_data: Structured prescription data

        Returns:
            Formatted prescription text
        """
        template = f"""
PRESCRIPTION

Doctor Information:
Name: {prescription_data.get('doctor', {}).get('name', 'N/A')}
License: {prescription_data.get('doctor', {}).get('license', 'N/A')}
Clinic: {prescription_data.get('doctor', {}).get('clinic', 'N/A')}
Contact: {prescription_data.get('doctor', {}).get('contact', 'N/A')}

Patient Information:
Name: {prescription_data.get('patient', {}).get('name', 'N/A')}
Age: {prescription_data.get('patient', {}).get('age', 'N/A')}
Gender: {prescription_data.get('patient', {}).get('gender', 'N/A')}
Patient ID: {prescription_data.get('patient', {}).get('id', 'N/A')}

Date: {prescription_data.get('date', 'N/A')}
Diagnosis: {prescription_data.get('diagnosis', 'N/A')}

MEDICATIONS:
"""

        medications = prescription_data.get('medications', [])
        for idx, med in enumerate(medications, 1):
            template += f"""
{idx}. {med.get('name', 'N/A')} {f"({med.get('brand_name')})" if med.get('brand_name') else ''}
   Dosage: {med.get('dosage', 'N/A')}
   Frequency: {med.get('frequency', 'N/A')}
   Duration: {med.get('duration', 'N/A')}
   Quantity: {med.get('quantity', 'N/A')}
   Route: {med.get('route', 'Oral')}
   Instructions: {med.get('instructions', 'N/A')}
"""

        template += f"""
Additional Notes:
{prescription_data.get('additional_notes', 'None')}

Follow-up:
{prescription_data.get('follow_up', 'None')}
"""

        if prescription_data.get('unclear_portions'):
            template += f"\nUnclear Portions (Please Review):\n"
            for item in prescription_data.get('unclear_portions', []):
                template += f"- {item}\n"

        return template.strip()

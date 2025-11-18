"""
AI-Powered Patient Data Embedding Agent using Google ADK
Creates embeddings for patient data for semantic search and retrieval
"""
import os
from typing import Dict, Any, List, Optional
import json
from datetime import datetime

from google import genai
from google.genai import types


class PatientEmbeddingAgent:
    """
    AI Agent for creating embeddings of patient data.
    Uses Google ADK's embedding capabilities for semantic search.
    """

    def __init__(self, api_key: str):
        """
        Initialize the patient embedding agent.

        Args:
            api_key: Google API key
        """
        self.client = genai.Client(api_key=api_key)
        self.embedding_model = "models/text-embedding-004"

    def _prepare_patient_document(
        self,
        patient_data: Dict[str, Any],
        medical_history: List[Dict[str, Any]]
    ) -> str:
        """
        Prepare a comprehensive text document from patient data.

        Args:
            patient_data: Patient demographic and basic info
            medical_history: List of medical history records

        Returns:
            Formatted text document
        """
        # Build patient profile section
        doc = f"""
PATIENT PROFILE
===============
Name: {patient_data.get('first_name', '')} {patient_data.get('last_name', '')}
Age: {patient_data.get('age', 'N/A')}
Gender: {patient_data.get('gender', 'N/A')}
Blood Group: {patient_data.get('blood_group', 'N/A')}
Contact: {patient_data.get('phone', 'N/A')}
Email: {patient_data.get('email', 'N/A')}
Address: {patient_data.get('address', 'N/A')}
Emergency Contact: {patient_data.get('emergency_contact_name', 'N/A')} - {patient_data.get('emergency_contact_phone', 'N/A')}

ALLERGIES: {', '.join(patient_data.get('allergies', [])) if patient_data.get('allergies') else 'None reported'}
CHRONIC CONDITIONS: {', '.join(patient_data.get('chronic_conditions', [])) if patient_data.get('chronic_conditions') else 'None reported'}

MEDICAL HISTORY
===============
"""

        # Add medical history records
        if medical_history:
            for idx, record in enumerate(medical_history, 1):
                doc += f"\n--- Visit {idx} ---\n"
                doc += f"Date: {record.get('visit_date', 'N/A')}\n"
                doc += f"Doctor: {record.get('doctor_name', 'N/A')}\n"
                doc += f"Diagnosis: {record.get('diagnosis', 'N/A')}\n"
                doc += f"Symptoms: {', '.join(record.get('symptoms', [])) if record.get('symptoms') else 'N/A'}\n"

                # Add prescriptions
                if record.get('prescriptions'):
                    doc += "\nPrescriptions:\n"
                    for med in record.get('prescriptions', []):
                        doc += f"  - {med.get('medication_name', 'N/A')}: {med.get('dosage', 'N/A')}, {med.get('frequency', 'N/A')}\n"
                        if med.get('instructions'):
                            doc += f"    Instructions: {med.get('instructions')}\n"

                doc += f"\nNotes: {record.get('notes', 'N/A')}\n"
                doc += f"Treatment: {record.get('treatment', 'N/A')}\n"

                # Add vital signs if present
                if record.get('blood_pressure'):
                    doc += f"Blood Pressure: {record.get('blood_pressure')}\n"
                if record.get('heart_rate'):
                    doc += f"Heart Rate: {record.get('heart_rate')}\n"
                if record.get('temperature'):
                    doc += f"Temperature: {record.get('temperature')}\n"
                if record.get('weight'):
                    doc += f"Weight: {record.get('weight')}\n"
                if record.get('height'):
                    doc += f"Height: {record.get('height')}\n"
        else:
            doc += "No medical history records available.\n"

        return doc.strip()

    async def create_patient_embedding(
        self,
        patient_data: Dict[str, Any],
        medical_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create an embedding for patient data.

        Args:
            patient_data: Patient demographic and basic info
            medical_history: List of medical history records

        Returns:
            Dictionary with embedding vector and metadata
        """
        try:
            # Prepare comprehensive patient document
            patient_document = self._prepare_patient_document(patient_data, medical_history)

            # Create embedding
            response = self.client.models.embed_content(
                model=self.embedding_model,
                content=patient_document,
                config=types.EmbedContentConfig(
                    task_type="retrieval_document",
                    title=f"Patient: {patient_data.get('first_name', '')} {patient_data.get('last_name', '')}"
                )
            )

            return {
                "patient_id": patient_data.get("patient_id"),
                "embedding": response.embeddings[0].values,
                "document": patient_document,
                "metadata": {
                    "patient_name": f"{patient_data.get('first_name', '')} {patient_data.get('last_name', '')}",
                    "total_visits": len(medical_history),
                    "chronic_conditions": patient_data.get('chronic_conditions', []),
                    "allergies": patient_data.get('allergies', []),
                    "last_updated": datetime.utcnow().isoformat()
                }
            }

        except Exception as e:
            print(f"Error creating patient embedding: {str(e)}")
            return {
                "error": str(e),
                "patient_id": patient_data.get("patient_id"),
                "embedding": None
            }

    async def create_query_embedding(self, query: str) -> List[float]:
        """
        Create an embedding for a search query.

        Args:
            query: The search query text

        Returns:
            Embedding vector
        """
        try:
            response = self.client.models.embed_content(
                model=self.embedding_model,
                content=query,
                config=types.EmbedContentConfig(
                    task_type="retrieval_query"
                )
            )

            return response.embeddings[0].values

        except Exception as e:
            print(f"Error creating query embedding: {str(e)}")
            return []

    async def batch_create_embeddings(
        self,
        patients_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Create embeddings for multiple patients.

        Args:
            patients_data: List of patient data with medical history

        Returns:
            List of embedding results
        """
        results = []

        for patient_info in patients_data:
            patient_data = patient_info.get("patient_data", {})
            medical_history = patient_info.get("medical_history", [])

            embedding_result = await self.create_patient_embedding(
                patient_data,
                medical_history
            )
            results.append(embedding_result)

        return results

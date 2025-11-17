"""
RecordAgent - Specialized agent for fetching and summarizing patient records
"""
import json
from typing import Dict, Any, Optional, AsyncGenerator
from datetime import datetime
import anthropic

from .config import get_system_prompt, get_general_config, get_agent_config
from .tools.postgres_tools import (
    query_patient_records,
    query_patient_by_id,
    query_health_vitals,
    query_prescriptions,
    query_medical_reports,
    TOOLS
)


class RecordAgent:
    """
    Specialized AI agent for analyzing and summarizing patient medical records
    Uses temperature 0.1 for deterministic, focused responses
    """

    def __init__(
        self,
        api_key: str,
        model: Optional[str] = None,
        temperature: float = 0.1
    ):
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.config = get_general_config()
        self.agent_config = get_agent_config('record_agent')

        # Use config defaults if not specified
        self.model = model or self.config.get('model', 'claude-3-5-sonnet-20241022')
        self.temperature = temperature  # Always 0.1 for record analysis
        self.max_tokens = self.config.get('max_tokens', 4096)

        # System prompt
        self.system_prompt = get_system_prompt('record_agent')

        # Available tools
        self.tools = TOOLS
        self.tool_functions = {
            'query_patient_by_id': query_patient_by_id,
            'query_patient_records': query_patient_records,
            'query_health_vitals': query_health_vitals,
            'query_prescriptions': query_prescriptions,
            'query_medical_reports': query_medical_reports,
        }

    async def process_tool_call(self, tool_name: str, tool_input: Dict[str, Any]) -> Any:
        """Execute a tool call"""
        if tool_name in self.tool_functions:
            func = self.tool_functions[tool_name]
            return await func(**tool_input)
        else:
            return {"error": f"Unknown tool: {tool_name}"}

    async def get_patient_summary(
        self,
        patient_id: str,
        stream: bool = False
    ) -> AsyncGenerator[str, None]:
        """
        Get a comprehensive summary of patient records

        Args:
            patient_id: The patient's unique identifier
            stream: Whether to stream the response

        Yields:
            Summary chunks if streaming, otherwise yields complete summary
        """
        # First, fetch the patient records using tools
        try:
            patient_data = await query_patient_records(patient_id, limit=100)

            if "error" in patient_data:
                yield self.agent_config.get('no_records_message', 'No records found.')
                return

            # Format the data for the AI to summarize
            data_context = self._format_patient_data(patient_data)

            # Create the analysis prompt
            analysis_prompt = f"""
Please provide a comprehensive summary of this patient's medical records.

{data_context}

Please structure your summary following these sections:
1. Patient Overview
2. Critical Medical Information (allergies, chronic conditions)
3. Recent Health Status (vitals, active prescriptions)
4. Medical History Summary
5. Key Observations and Recommendations

Use clear, professional language suitable for both healthcare providers and patients.
"""

            messages = [{
                "role": "user",
                "content": analysis_prompt
            }]

            if stream:
                async with self.client.messages.stream(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    system=self.system_prompt,
                    messages=messages,
                ) as response_stream:
                    async for event in response_stream:
                        if hasattr(event, 'type') and event.type == 'content_block_delta':
                            if hasattr(event.delta, 'type') and event.delta.type == 'text_delta':
                                yield event.delta.text
            else:
                response = await self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    system=self.system_prompt,
                    messages=messages,
                )

                response_text = ""
                for block in response.content:
                    if hasattr(block, 'text'):
                        response_text += block.text

                yield response_text

        except Exception as e:
            error_message = f"Error retrieving patient records: {str(e)}"
            yield error_message

    async def analyze_vitals(
        self,
        patient_id: str,
        vital_type: Optional[str] = None,
        days: int = 30,
        stream: bool = False
    ) -> AsyncGenerator[str, None]:
        """
        Analyze patient's health vitals with AI insights

        Args:
            patient_id: The patient's unique identifier
            vital_type: Optional specific vital type to analyze
            days: Number of days to look back
            stream: Whether to stream the response

        Yields:
            Analysis chunks if streaming, otherwise yields complete analysis
        """
        try:
            # Calculate date range
            from datetime import timedelta
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)

            vitals = await query_health_vitals(
                patient_id=patient_id,
                vital_type=vital_type,
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat(),
                limit=200
            )

            if not vitals:
                yield "No vital signs data available for the specified period."
                return

            # Format vitals data
            vitals_text = self._format_vitals_data(vitals)

            analysis_prompt = f"""
Analyze the following health vitals data:

{vitals_text}

Please provide:
1. Summary of vital signs trends
2. Identification of any concerning patterns or outliers
3. Comparison with normal ranges where applicable
4. Clinical significance of the findings

Be factual, precise, and highlight anything that may require medical attention.
"""

            messages = [{
                "role": "user",
                "content": analysis_prompt
            }]

            if stream:
                async with self.client.messages.stream(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    system=self.system_prompt,
                    messages=messages,
                ) as response_stream:
                    async for event in response_stream:
                        if hasattr(event, 'type') and event.type == 'content_block_delta':
                            if hasattr(event.delta, 'type') and event.delta.type == 'text_delta':
                                yield event.delta.text
            else:
                response = await self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    system=self.system_prompt,
                    messages=messages,
                )

                response_text = ""
                for block in response.content:
                    if hasattr(block, 'text'):
                        response_text += block.text

                yield response_text

        except Exception as e:
            error_message = f"Error analyzing vitals: {str(e)}"
            yield error_message

    async def summarize_prescriptions(
        self,
        patient_id: str,
        stream: bool = False
    ) -> AsyncGenerator[str, None]:
        """
        Summarize patient's prescriptions with medication information

        Args:
            patient_id: The patient's unique identifier
            stream: Whether to stream the response

        Yields:
            Summary chunks if streaming, otherwise yields complete summary
        """
        try:
            prescriptions = await query_prescriptions(
                patient_id=patient_id,
                active_only=True,
                limit=50
            )

            if not prescriptions:
                yield "No active prescriptions found for this patient."
                return

            # Format prescription data
            prescriptions_text = self._format_prescriptions_data(prescriptions)

            summary_prompt = f"""
Summarize the following prescriptions for the patient:

{prescriptions_text}

Please provide:
1. List of active medications with dosage and purpose
2. Prescribing doctors and specializations
3. Any potential drug interactions or concerns (if obvious)
4. Medication adherence recommendations

Keep the summary clear and organized.
"""

            messages = [{
                "role": "user",
                "content": summary_prompt
            }]

            if stream:
                async with self.client.messages.stream(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    system=self.system_prompt,
                    messages=messages,
                ) as response_stream:
                    async for event in response_stream:
                        if hasattr(event, 'type') and event.type == 'content_block_delta':
                            if hasattr(event.delta, 'type') and event.delta.type == 'text_delta':
                                yield event.delta.text
            else:
                response = await self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    system=self.system_prompt,
                    messages=messages,
                )

                response_text = ""
                for block in response.content:
                    if hasattr(block, 'text'):
                        response_text += block.text

                yield response_text

        except Exception as e:
            error_message = f"Error summarizing prescriptions: {str(e)}"
            yield error_message

    def _format_patient_data(self, patient_data: Dict[str, Any]) -> str:
        """Format patient data for AI analysis"""
        patient = patient_data.get('patient', {})
        vitals = patient_data.get('vitals', [])
        prescriptions = patient_data.get('prescriptions', [])
        reports = patient_data.get('reports', [])

        formatted = f"""
PATIENT INFORMATION:
Name: {patient.get('first_name')} {patient.get('last_name')}
Age: {patient.get('age')} years
Gender: {patient.get('gender')}
Blood Type: {patient.get('blood_type', 'N/A')}
Allergies: {json.dumps(patient.get('allergies', []))}
Chronic Conditions: {json.dumps(patient.get('chronic_conditions', []))}

RECENT HEALTH VITALS ({len(vitals)} records):
"""
        for vital in vitals[:10]:  # Show most recent 10
            formatted += f"- {vital['vital_type']}: {vital['value']} {vital['unit']} (recorded: {vital['recorded_at']})\n"

        formatted += f"\nACTIVE PRESCRIPTIONS ({len(prescriptions)} total):\n"
        for rx in prescriptions[:10]:
            formatted += f"""
- Medications: {json.dumps(rx['medications'])}
  Diagnosis: {rx.get('diagnosis', 'N/A')}
  Prescribed by: Dr. {rx.get('doctor_first_name')} {rx.get('doctor_last_name')} ({rx.get('specialization')})
  Date: {rx['prescribed_date']}
"""

        formatted += f"\nMEDICAL REPORTS ({len(reports)} total):\n"
        for report in reports[:10]:
            formatted += f"""
- {report['title']} ({report['report_type']})
  Date: {report['report_date']}
  Doctor: Dr. {report.get('doctor_first_name')} {report.get('doctor_last_name')}
"""

        return formatted

    def _format_vitals_data(self, vitals: list) -> str:
        """Format vitals data for analysis"""
        formatted = "Health Vitals Records:\n\n"
        for vital in vitals:
            formatted += f"- {vital['vital_type']}: {vital['value']} {vital['unit']} "
            formatted += f"(recorded: {vital['recorded_at']})\n"
            if vital.get('notes'):
                formatted += f"  Notes: {vital['notes']}\n"
        return formatted

    def _format_prescriptions_data(self, prescriptions: list) -> str:
        """Format prescription data for summary"""
        formatted = "Active Prescriptions:\n\n"
        for rx in prescriptions:
            formatted += f"Prescription ID: {rx['prescription_id']}\n"
            formatted += f"Medications: {json.dumps(rx['medications'], indent=2)}\n"
            formatted += f"Diagnosis: {rx.get('diagnosis', 'N/A')}\n"
            formatted += f"Prescribed by: Dr. {rx.get('doctor_first_name')} {rx.get('doctor_last_name')}\n"
            formatted += f"Specialization: {rx.get('specialization', 'N/A')}\n"
            formatted += f"Date: {rx['prescribed_date']}\n"
            formatted += f"Valid until: {rx.get('valid_until', 'Ongoing')}\n"
            if rx.get('notes'):
                formatted += f"Notes: {rx['notes']}\n"
            formatted += "\n"
        return formatted

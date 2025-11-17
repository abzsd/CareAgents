import json
from typing import Dict, Any, Optional, AsyncGenerator
from datetime import datetime, timedelta

from google.adk.agents.llm_agent import Agent
from google.adk.models import AgentOutput, ToolCode, ToolOutput

from ..config import get_system_prompt, get_general_config, get_agent_config
from ..adk_tools import (
    query_patient_records,
    query_patient_by_id,
    query_health_vitals,
    query_prescriptions,
    query_medical_reports
)


class AdkRecordAgent:
    """
    Specialized AI agent for analyzing and summarizing patient records,
    built using Google's Agent Development Kit (ADK).
    Uses temperature 0.1 for deterministic, focused responses.
    """

    def __init__(
        self,
        model: Optional[str] = None,
        temperature: float = 0.1
    ):
        self.config = get_general_config()
        self.agent_config = get_agent_config('record_agent')

        self.model = model or "gemini-2.5-flash" # Default to gemini-2.5-flash
        self.temperature = temperature  # Always 0.1 for record analysis
        self.max_tokens = self.config.get('max_tokens', 4096)

        self.system_prompt = get_system_prompt('record_agent')

        # Define tools for the ADK agent
        self.tools = [
            query_patient_by_id,
            query_patient_records,
            query_health_vitals,
            query_prescriptions,
            query_medical_reports,
        ]

        # Initialize the ADK Agent
        self.adk_agent = Agent(
            model=self.model,
            name='RecordAgent',
            description='A specialized AI agent for analyzing and summarizing patient medical records.',
            instruction=self.system_prompt,
            tools=self.tools,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

    async def get_patient_summary(
        self,
        patient_id: str,
        stream: bool = False
    ) -> AsyncGenerator[str, None]:
        """
        Get a comprehensive summary of patient records using the ADK agent.
        """
        try:
            # First, fetch the patient records using tools directly or let the agent decide
            # For now, we'll let the agent decide by providing the prompt.
            # The agent will use query_patient_records tool.

            data_context = ""
            # We need to make an initial call to the agent to get the patient data
            # or call the tool directly and then pass the data to the agent.
            # For simplicity, let's assume the agent will call the tool.

            messages = [{
                "role": "user",
                "content": f"Please provide a comprehensive summary of patient records for patient ID: {patient_id}."
            }]

            full_response_content = ""
            async for agent_output in self.adk_agent.generate_response(
                messages=messages,
                stream=True
            ):
                if isinstance(agent_output, AgentOutput):
                    if agent_output.text:
                        full_response_content += agent_output.text
                        if stream:
                            yield agent_output.text
                    if agent_output.tool_code:
                        tool_code: ToolCode = agent_output.tool_code
                        tool_name = tool_code.name
                        tool_input = tool_code.args

                        tool_result = await self._execute_tool(tool_name, tool_input)

                        tool_output = ToolOutput(tool_code=tool_code, output=tool_result)
                        async for final_output in self.adk_agent.generate_response(
                            messages=messages + [{"role": "assistant", "content": [tool_code.to_dict()]}, {"role": "user", "content": [tool_output.to_dict()]}],
                            stream=True
                        ):
                            if isinstance(final_output, AgentOutput) and final_output.text:
                                full_response_content += final_output.text
                                if stream:
                                    yield final_output.text

            if not stream:
                yield full_response_content

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
        Analyze patient's health vitals with AI insights using the ADK agent.
        """
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)

            prompt_content = f"Analyze health vitals for patient ID: {patient_id} from {start_date.isoformat()} to {end_date.isoformat()}."
            if vital_type:
                prompt_content += f" Focus on {vital_type}."

            messages = [{
                "role": "user",
                "content": prompt_content
            }]

            full_response_content = ""
            async for agent_output in self.adk_agent.generate_response(
                messages=messages,
                stream=True
            ):
                if isinstance(agent_output, AgentOutput):
                    if agent_output.text:
                        full_response_content += agent_output.text
                        if stream:
                            yield agent_output.text
                    if agent_output.tool_code:
                        tool_code: ToolCode = agent_output.tool_code
                        tool_name = tool_code.name
                        tool_input = tool_code.args

                        tool_result = await self._execute_tool(tool_name, tool_input)

                        tool_output = ToolOutput(tool_code=tool_code, output=tool_result)
                        async for final_output in self.adk_agent.generate_response(
                            messages=messages + [{"role": "assistant", "content": [tool_code.to_dict()]}, {"role": "user", "content": [tool_output.to_dict()]}],
                            stream=True
                        ):
                            if isinstance(final_output, AgentOutput) and final_output.text:
                                full_response_content += final_output.text
                                if stream:
                                    yield final_output.text

            if not stream:
                yield full_response_content

        except Exception as e:
            error_message = f"Error analyzing vitals: {str(e)}"
            yield error_message

    async def summarize_prescriptions(
        self,
        patient_id: str,
        stream: bool = False
    ) -> AsyncGenerator[str, None]:
        """
        Summarize patient's prescriptions with medication information using the ADK agent.
        """
        try:
            prompt_content = f"Summarize active prescriptions for patient ID: {patient_id}."

            messages = [{
                "role": "user",
                "content": prompt_content
            }]

            full_response_content = ""
            async for agent_output in self.adk_agent.generate_response(
                messages=messages,
                stream=True
            ):
                if isinstance(agent_output, AgentOutput):
                    if agent_output.text:
                        full_response_content += agent_output.text
                        if stream:
                            yield agent_output.text
                    if agent_output.tool_code:
                        tool_code: ToolCode = agent_output.tool_code
                        tool_name = tool_code.name
                        tool_input = tool_code.args

                        tool_result = await self._execute_tool(tool_name, tool_input)

                        tool_output = ToolOutput(tool_code=tool_code, output=tool_result)
                        async for final_output in self.adk_agent.generate_response(
                            messages=messages + [{"role": "assistant", "content": [tool_code.to_dict()]}, {"role": "user", "content": [tool_output.to_dict()]}],
                            stream=True
                        ):
                            if isinstance(final_output, AgentOutput) and final_output.text:
                                full_response_content += final_output.text
                                if stream:
                                    yield final_output.text

            if not stream:
                yield full_response_content

        except Exception as e:
            error_message = f"Error summarizing prescriptions: {str(e)}"
            yield error_message

    async def _execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Any:
        """Execute a tool call based on its name and input."""
        tool_function = next((t for t in self.tools if t.__name__ == tool_name), None)
        if tool_function:
            return await tool_function(**tool_input)
        else:
            return {"error": f"Unknown tool: {tool_name}"}

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

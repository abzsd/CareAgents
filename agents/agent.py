from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.tools import agent_tool
from google.adk.tools import langchain_tool

from .custom_functions import get_fx_rate
from .custom_agents import google_search_agent
from .third_party_tools import langchain_wikipedia_tool

root_agent = Agent(
    model='gemini-2.0-flash-001',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge',
    tools=[]
)

import os
from typing import List, Dict, Any, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from google.cloud import firestore
from google.adk.agents import LlmAgent
from google.genai import types as genai_types

# -------------------------------------------------------------------
# ENV + GOOGLE CLIENTS
# -------------------------------------------------------------------

# Example env vars (set these in your environment / .env)
# os.environ["GOOGLE_API_KEY"] = "YOUR_API_KEY"
# os.environ["GOOGLE_CLOUD_PROJECT"] = "your-gcp-project-id"

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "your-gcp-project-id")
GEMINI_MODEL = "gemini-2.0-flash"  # or gemini-2.0-pro for heavier summaries

# Firestore client (Google database)
db = firestore.Client(project=PROJECT_ID)

# -------------------------------------------------------------------
# DATA ACCESS HELPERS (used as tools by agents)
# -------------------------------------------------------------------

def _get_patient_doc(patient_id: str) -> Optional[Dict[str, Any]]:
    """Low-level helper to fetch patient root document."""
    doc_ref = db.collection("patients").document(patient_id)
    doc = doc_ref.get()
    if not doc.exists:
        return None
    return doc.to_dict()


def _get_subcollection_docs(patient_id: str, subcollection: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Fetches documents from a patient's subcollection (visits, labs, imaging, prescriptions, etc.)."""
    coll_ref = db.collection("patients").document(patient_id).collection(subcollection)
    # Example: most recent first using a 'timestamp' field
    docs = (
        coll_ref.order_by("timestamp", direction=firestore.Query.DESCENDING)
        .limit(limit)
        .stream()
    )
    result = []
    for d in docs:
        data = d.to_dict()
        data["id"] = d.id
        data["collection"] = subcollection
        result.append(data)
    return result


# -------------------------------------------------------------------
# TOOL FUNCTIONS (ADK wraps these into tools automatically in Python)
# -------------------------------------------------------------------

def fetch_patient_context(patient_id: str) -> Dict[str, Any]:
    """
    Fetch core patient context:
    demographics, allergies, active problems, medications + latest labs & imaging.
    Returned structure is used by Patient Context Builder agent.
    """
    patient = _get_patient_doc(patient_id)
    if not patient:
        raise ValueError(f"Patient {patient_id} not found")

    # customize keys based on your schema
    demographics = patient.get("demographics", {})
    allergies = patient.get("allergies", [])
    problems = patient.get("problems", [])
    medications = patient.get("medications", [])

    latest_labs = _get_subcollection_docs(patient_id, "labs", limit=10)
    latest_imaging = _get_subcollection_docs(patient_id, "imaging", limit=10)

    return {
        "patient_id": patient_id,
        "demographics": demographics,
        "allergies": allergies,
        "problems": problems,
        "medications": medications,
        "latest_labs": latest_labs,
        "latest_imaging": latest_imaging,
    }


def fetch_previous_reports(patient_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Fetch previous OPD notes / discharge summaries / follow-up notes.
    Each note must include timestamps and references to source reports if possible.
    """
    reports = _get_subcollection_docs(patient_id, "reports", limit=limit)
    return reports


def save_doctor_summary(
    patient_id: str,
    summary_markdown: str,
    structured_json: Dict[str, Any],
) -> str:
    """
    Save the generated summary for this visit into the 'summaries' subcollection.
    Returns summary document ID.
    """
    coll_ref = db.collection("patients").document(patient_id).collection("summaries")
    doc_ref = coll_ref.document()
    payload = {
        "summary_markdown": summary_markdown,
        "structured_summary": structured_json,
        "created_at": datetime.utcnow().isoformat() + "Z",
    }
    doc_ref.set(payload)
    return doc_ref.id


# -------------------------------------------------------------------
# AGENT DEFINITIONS (multi-agent, event-driven-ish orchestration)
# -------------------------------------------------------------------

# 1) Patient Context Builder Agent
patient_context_agent = Agent(
    name="patient_context_builder",
    model="gemini-2.0-flash-001",
    description="Aggregates patient context from EHR and lab/imaging sources.",
    instruction="""
You are the Patient Context Builder for an OPD assistant.

Your job:
- Use the tools to fetch data for the given patient_id.
- Produce a concise, structured JSON object named `patient_context` with:
  - demographics
  - key problems
  - allergies
  - current medications
  - latest significant lab and imaging results

Important:
- Do NOT invent data.
- Only use what the tools return.
- Keep output machine-readable JSON with short, clinically useful text, not paragraphs.
    """,
    tools=[fetch_patient_context],
)

# 2) History + Redundancy Analyzer Agent
history_dedup_agent = LlmAgent(
    name="history_dedup_agent",
    model=GEMINI_MODEL,
    description="Categorizes historical reports and flags redundant info.",
    instruction="""
You are a History & Redundancy Analyzer for OPD notes.

Input:
- Previous clinical documents for the same patient (OPD notes, discharge summaries, follow-ups).

Your tasks:
1. Categorize past documents by type (e.g., 'OPD note', 'Discharge summary', 'Follow-up').
2. Identify key longitudinal developments (what changed over time).
3. Detect repeated or duplicated content across notes.
4. Flag redundancy: indicate which clinical facts are repeated in many reports.
5. Output:
   - `timeline` (ordered by date, with short bullet descriptions)
   - `redundant_facts` (facts that appear multiple times, with a `frequency` count)
   - `unique_recent_changes` (things only appearing in the latest 1–2 reports)
   - Each item should include references: `source_ids` list of report IDs.

STRICT RULES:
- Don't modify or hide clinical facts; only *label* redundancy.
- Don't provide diagnosis or treatment advice.
- Everything must be traceable to one or more source report IDs.
Output strict JSON.
    """,
    tools=[fetch_previous_reports],
)

# 3) Clinical Summarizer Agent
clinical_summarizer_agent = LlmAgent(
    name="clinical_summarizer_agent",
    model=GEMINI_MODEL,
    description="Generates a doctor-facing OPD summary with transparent citations.",
    instruction="""
You are the Clinical Summarizer for an OPD assistant.

You receive:
- `patient_context` (from Patient Context Builder agent)
- `timeline`, `redundant_facts`, `unique_recent_changes` (from History & Redundancy Analyzer)

Your task:
- Generate a *doctor-facing* summary for the current OPD visit.
- It must be:
  - Brief and clinically focused.
  - Non-diagnostic: DO NOT infer or suggest diagnoses or treatments.
  - Fully citation-aware: every clinical statement must reference its data source IDs.

Output format (JSON):
{
  "current_opd_summary": {
    "chief_complaint": "...",
    "history_of_present_illness": "...",
    "relevant_past_history": "...",
    "medications_overview": "...",
    "key_lab_and_imaging": "...",
    "assessment_style_note": "Plain-language but non-diagnostic summary.",
    "citations": [
      {
        "statement_id": "hpi_1",
        "text": "Short statement...",
        "source_ids": ["lab:abc123", "report:xyz789"]
      }
    ]
  }
}

Rules:
- Do NOT add new facts.
- Use the source IDs from:
  - labs/imaging returned in patient_context (id fields),
  - previous reports (id fields),
  - and any other structured arrays.
- Keep output valid JSON with double quotes and no trailing commas.
    """,
    tools=[],
)

# 4) Root Orchestrator Agent (for doctor screen)
doctor_view_agent = LlmAgent(
    name="doctor_view_orchestrator",
    model=GEMINI_MODEL,
    description="Orchestrates context building, history analysis, and summarization for doctor view.",
    instruction="""
You are the orchestrator for a multi-agent OPD assistant.

High-level goal:
- Given a patient_id, prepare a single JSON payload for the doctor screen that includes:
  - `patient_context` (from patient_context_builder)
  - `history_overview` (from history_dedup_agent)
  - `current_opd_summary` (from clinical_summarizer_agent)

How to work:
1. Call the `patient_context_builder` sub-agent first using the patient_id.
2. Then call `history_dedup_agent` to get `timeline` and redundancy info.
3. Give both outputs to `clinical_summarizer_agent` to generate the final summary.
4. Merge everything into a single JSON:
{
  "patient_context": {...},
  "history_overview": {
     "timeline": [...],
     "redundant_facts": [...],
     "unique_recent_changes": [...]
  },
  "current_opd_summary": {...}
}

Constraints:
- This system is for DOCTOR USE ONLY. No direct patient advice.
- Do not infer diagnoses or prescribe treatment.
- Ensure all narrative content includes clear references to source ids where possible.
- Never output markdown, only JSON.
    """,
    # Sub-agents are used as tools / delegated agents
    sub_agents=[
        patient_context_agent,
        history_dedup_agent,
        clinical_summarizer_agent,
    ],
)


# -------------------------------------------------------------------
# FASTAPI BACKEND – DOCTOR SCREEN ENDPOINT
# -------------------------------------------------------------------

app = FastAPI(title="OPD Multi-Agent Backend")


class DoctorViewRequest(BaseModel):
    patient_id: str
    # Optional: current visit metadata, if you want
    visit_id: Optional[str] = None
    save_summary: bool = True


class DoctorViewResponse(BaseModel):
    patient_id: str
    payload: Dict[str, Any]
    saved_summary_id: Optional[str] = None


@app.post("/doctor/patient-view", response_model=DoctorViewResponse)
def get_doctor_view(req: DoctorViewRequest):
    """
    Main backend endpoint for the doctor screen.

    It:
    - Triggers the orchestrator agent.
    - Returns a unified JSON payload for the UI.
    - Optionally saves the generated summary back to Firestore.
    """
    # 1. Build a textual instruction for the root agent.
    # (You could also use input_schema for stricter structure.)
    orchestrator_prompt = f"""
You are the doctor_view_orchestrator.
The patient_id is "{req.patient_id}".
Produce the JSON structure described in your instruction.
    """.strip()

    try:
        # Basic synchronous run – in real app, consider Runner + sessions for streaming.
        result = doctor_view_agent.run(orchestrator_prompt)

        # ADK may return a Content / string; assume string JSON here for simplicity.
        if isinstance(result, str):
            import json
            payload = json.loads(result)
        else:
            # For some configurations, `result` might be a dict-like already.
            # Try to normalize:
            try:
                payload = dict(result)  # type: ignore
            except Exception:
                raise ValueError(
                    f"Unexpected agent output type: {type(result)}. "
                    "Ensure doctor_view_orchestrator returns JSON text."
                )

        saved_summary_id = None
        if req.save_summary:
            # Pull summary and save to DB so it appears in future context/history.
            summary = payload.get("current_opd_summary", {})
            summary_markdown = summary.get("assessment_style_note", "")
            saved_summary_id = save_doctor_summary(
                patient_id=req.patient_id,
                summary_markdown=summary_markdown,
                structured_json=summary,
            )

        return DoctorViewResponse(
            patient_id=req.patient_id,
            payload=payload,
            saved_summary_id=saved_summary_id,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------------------
# LOCAL DEV ENTRYPOINT
# -------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)

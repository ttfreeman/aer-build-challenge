"""Minimal shared data models."""
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field


class Extraction(BaseModel):
    reporter_name: Optional[str] = None
    reporter_contact: Optional[str] = None
    operator_named: Optional[str] = None
    location_text: Optional[str] = None
    timestamp_incident: Optional[str] = None
    substance_or_hazard: Optional[str] = None
    observed_symptoms: Optional[str] = None
    summary_of_events: str = ""


class RegulatoryFinding(BaseModel):
    directive_id: Optional[str] = None
    clause_reference: Optional[str] = None
    finding_summary: str = ""


class TriageResult(BaseModel):
    record_id: str
    extraction: Extraction
    severity_tier: Literal["Tier 1", "Tier 2", "Tier 3", "Tier 4", "Untiered"]
    tier_reasoning: str
    regulatory_finding: RegulatoryFinding
    route: Literal[
        "Escalate to duty officer",
        "Queue for inspection",
        "Assign to operator liaison",
        "Acknowledge and close",
        "Records only",
        "Callback queue"
    ]
    human_flag: bool
    human_flag_reason: Optional[str] = None
    run_record: Dict[str, Any]


class ValidationOverride(BaseModel):
    rule: str
    detail: str
    previous_tier: Optional[str] = None
    new_tier: Optional[str] = None

"""Triage engine: orchestrate the pipeline."""
import os
from datetime import datetime, timezone
from typing import Dict, Any
from pathlib import Path

from src.models import TriageResult
from src.sanitizer import sanitize
from src.extract import extract
from src.classifier import classify
from src.validator import validate
from src.router import route
from src.trace import build_trace, write_trace


class TriageEngine:
    def __init__(self, traces_dir: Path = Path("traces")):
        self.traces_dir = traces_dir
    
    def process_record(self, record: Dict[str, Any]) -> TriageResult:
        """Process a single intake record through the full pipeline."""
        start_time = datetime.now(timezone.utc)
        record_id = record["record_id"]
        raw_text = record.get("raw_text", "")
        
        # Pipeline stages
        sanitized_text, has_pii, has_injection = sanitize(raw_text)
        extraction = extract(record, sanitized_text)
        proposed_tier, proposed_reasoning, proposed_finding = classify(sanitized_text, extraction)
        
        # Validation & correction
        final_tier, final_reasoning, final_finding, overrides = validate(
            sanitized_text, extraction, proposed_tier, proposed_finding,
            has_pii, has_injection
        )
        
        # Routing
        is_records_only = any(o.rule == "compliant_self_report" for o in overrides)
        destination, human_flag, human_reason = route(final_tier, extraction, is_records_only)
        
        # Latency
        execution_latency = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        # Build output
        result = TriageResult(
            record_id=record_id,
            extraction=extraction,
            severity_tier=final_tier,
            tier_reasoning=final_reasoning,
            regulatory_finding=final_finding,
            route=destination,
            human_flag=human_flag,
            human_flag_reason=human_reason,
            run_record={
                "execution_timestamp_utc": start_time.isoformat(),
                "execution_latency_sec": round(execution_latency, 3),
                "sanitization": {"pii_redacted": has_pii, "injection_detected": has_injection},
                "validation_overrides": len(overrides)
            }
        )
        
        # Write trace
        trace = build_trace(
            record_id=record_id,
            extraction_dict=extraction.model_dump(),
            tier=final_tier,
            reasoning=final_reasoning,
            finding_dict=final_finding.model_dump(),
            route=destination,
            overrides=overrides,
            has_pii=has_pii,
            has_injection=has_injection,
            execution_latency_sec=execution_latency
        )
        write_trace(trace, self.traces_dir)
        
        return result

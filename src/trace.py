"""Trace: build and persist execution records."""
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List
from src.models import ValidationOverride


def build_trace(
    record_id: str,
    extraction_dict: Dict[str, Any],
    tier: str,
    reasoning: str,
    finding_dict: Dict[str, Any],
    route: str,
    overrides: List[ValidationOverride],
    has_pii: bool,
    has_injection: bool,
    execution_latency_sec: float
) -> Dict[str, Any]:
    """Build a complete execution trace."""
    
    return {
        "record_id": record_id,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "extraction": extraction_dict,
        "final_tier": tier,
        "tier_reasoning": reasoning,
        "regulatory_finding": finding_dict,
        "route": route,
        "overrides": [o.model_dump() for o in overrides],
        "security": {
            "pii_redacted": has_pii,
            "injection_detected": has_injection
        },
        "execution_latency_sec": round(execution_latency_sec, 3)
    }


def write_trace(trace: Dict[str, Any], traces_dir: Path) -> None:
    """Write trace to JSON file."""
    traces_dir.mkdir(parents=True, exist_ok=True)
    trace_path = traces_dir / f"{trace['record_id']}.json"
    trace_path.write_text(json.dumps(trace, indent=2), encoding="utf-8")

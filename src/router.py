"""Routing: map tier to destination and human gate."""
from src.models import Extraction


TIER_TO_ROUTE = {
    "Tier 1": "Escalate to duty officer",
    "Tier 2": "Queue for inspection",
    "Tier 3": "Assign to operator liaison",
    "Tier 4": "Acknowledge and close",
    "Untiered": "Callback queue",
}


def route(tier: str, extraction: Extraction, is_records_only: bool) -> tuple[str, bool, str]:
    """Return (destination, human_flag, human_reason)."""
    
    if is_records_only:
        return "Records only", False, ""
    
    route = TIER_TO_ROUTE.get(tier, "Queue for inspection")
    
    # Human gates
    human_flag = False
    human_reason = ""
    
    if tier == "Tier 1":
        human_flag = True
        human_reason = "Tier 1 life-safety event; never closed without named human decision."
    elif tier == "Untiered" and extraction.reporter_contact:
        human_flag = True
        human_reason = "Insufficient information to tier; callback verification required."
    
    return route, human_flag, human_reason

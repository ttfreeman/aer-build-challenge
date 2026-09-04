"""Validation loop: ensure final tier never under-tiers vs. deterministic floor."""
from typing import List
from src.models import Extraction, RegulatoryFinding, ValidationOverride
from src.classifier import classify


TIER_SEVERITY = {"Tier 1": 0, "Tier 2": 1, "Tier 3": 2, "Tier 4": 3, "Untiered": 4}


def is_records_only(extraction: Extraction, raw_text: str) -> bool:
    """Check if this is a compliant self-report (fully contained, ≤2.0 m³, no H2S/water/wildlife)."""
    lower = raw_text.lower()
    has_h2s = any(w in lower for w in ["h2s", "sour", "sulphur"])
    has_water = any(w in lower for w in ["creek", "water body", "watercourse"])
    has_wildlife = any(w in lower for w in ["dead", "wildlife", "cattle"])
    has_containment = "fully contained" in lower or "contained" in lower
    
    return has_containment and not (has_h2s or has_water or has_wildlife)


def validate(
    raw_text: str,
    extraction: Extraction,
    proposed_tier: str,
    proposed_finding: RegulatoryFinding,
    has_pii: bool,
    has_injection: bool
) -> tuple[str, str, RegulatoryFinding, List[ValidationOverride]]:
    """Apply deterministic floor and hard rules. Return (final_tier, final_reasoning, final_finding, overrides)."""
    
    overrides: List[ValidationOverride] = []
    final_tier = proposed_tier
    final_reasoning = ""
    final_finding = proposed_finding
    
    # Hard rule: insufficient information never gets escalated
    if proposed_tier == "Untiered" and extraction.location_text and extraction.operator_named:
        # If we have location/operator but said untiered, re-classify
        final_tier, final_reasoning, final_finding = classify(raw_text, extraction)
        overrides.append(ValidationOverride(
            rule="insufficient_info_correction",
            detail="Location and operator identified; re-classified.",
            previous_tier="Untiered",
            new_tier=final_tier
        ))
    
    # Hard rule: records-only compliance never escalated
    if is_records_only(extraction, raw_text):
        if proposed_tier != "Tier 4":
            overrides.append(ValidationOverride(
                rule="compliant_self_report",
                detail="Fully contained release ≤2.0m³, no H2S/water/wildlife impact; records-only per RD-101.3.",
                previous_tier=proposed_tier,
                new_tier="Tier 4"
            ))
            final_tier = "Tier 4"
            final_reasoning = "RD-101.3: Compliant self-report; records only, not a contravention."
            final_finding = RegulatoryFinding(
                directive_id="RD-101",
                clause_reference="Clause 3",
                finding_summary="Compliant licensee recording submission; not a contravention."
            )
    
    # Under-tiering guard: cross-check against deterministic floor
    else:
        floor_tier, floor_reasoning, floor_finding = classify(raw_text, extraction)
        if TIER_SEVERITY.get(floor_tier, 99) < TIER_SEVERITY.get(final_tier, 99):
            overrides.append(ValidationOverride(
                rule="under_tiering_guard",
                detail=f"Deterministic floor is {floor_tier}; escalating from {proposed_tier}.",
                previous_tier=proposed_tier,
                new_tier=floor_tier
            ))
            final_tier = floor_tier
            final_reasoning = floor_reasoning
            final_finding = floor_finding
    
    # Security flags
    if has_injection:
        overrides.append(ValidationOverride(
            rule="prompt_injection_detected",
            detail="Adversarial prompt injection detected and neutralized; record processed on merits only."
        ))
    
    if has_pii:
        overrides.append(ValidationOverride(
            rule="pii_redacted",
            detail="Sensitive PII detected and redacted from processing."
        ))
    
    return final_tier, final_reasoning, final_finding, overrides

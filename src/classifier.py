"""Classification: deterministic rule engine for tier assignment."""
from src.models import Extraction, RegulatoryFinding


def classify(raw_text: str, extraction: Extraction) -> tuple[str, str, RegulatoryFinding]:
    """Assign tier, reasoning, and regulatory finding.
    
    Returns: (tier, reasoning, RegulatoryFinding)
    """
    lower = raw_text.lower()
    
    # Insufficient info: no location and no operator
    if not extraction.location_text and not extraction.operator_named:
        return (
            "Untiered",
            "Insufficient info to establish jurisdiction.",
            RegulatoryFinding(directive_id=None, clause_reference=None, 
                            finding_summary="No location or operator identified.")
        )
    
    # Tier 1: H2S + health symptoms or watercourse
    if any(w in lower for w in ["h2s", "sour", "sulphur", "rotten egg"]):
        if any(w in lower for w in ["dizzy", "headache", "respiratory", "eyes watering"]):
            return (
                "Tier 1",
                "RD-101.1 & RD-114.3: H2S/sour gas with health symptoms; immediate escalation.",
                RegulatoryFinding(directive_id="RD-101", clause_reference="Clause 1",
                                finding_summary="H2S release with reported health impacts.")
            )
        if any(w in lower for w in ["creek", "water body", "watercourse", "drinking water"]):
            return (
                "Tier 1",
                "RD-101.1: H2S/sour gas reaching watercourse.",
                RegulatoryFinding(directive_id="RD-101", clause_reference="Clause 1",
                                finding_summary="H2S reaching watercourse.")
            )
    
    # Tier 1: Acute health symptoms
    if any(w in lower for w in ["dizzy", "dizziness", "headache", "respiratory", "clinic", "off school"]):
        return (
            "Tier 1",
            "RD-114.3: Potential health/life-safety risk; duty officer escalation required.",
            RegulatoryFinding(directive_id="RD-114", clause_reference="Clause 3",
                            finding_summary="Health or life-safety risk reported.")
        )
    
    # Tier 2: Wildlife mortality
    if any(w in lower for w in ["dead", "wildlife", "cattle", "songbirds"]):
        return (
            "Tier 2",
            "RD-101.4: Wildlife/livestock mortality reportable within 24h.",
            RegulatoryFinding(directive_id="RD-101", clause_reference="Clause 4",
                            finding_summary="Wildlife mortality associated with facility.")
        )
    
    # Tier 2: Unauthorized access
    if any(w in lower for w in ["without notice", "no notice", "gate left open"]):
        return (
            "Tier 2",
            "RD-146.2: Entry without mandatory 7-day notice is a contravention.",
            RegulatoryFinding(directive_id="RD-146", clause_reference="Clause 2",
                            finding_summary="Licensee entry without required notice.")
        )
    
    # Tier 2: Large release or water impact
    if any(w in lower for w in ["release", "spill", "dump"]):
        if any(w in lower for w in ["creek", "water body", "watercourse"]):
            return (
                "Tier 2",
                "RD-101.1: Liquid release reaching watercourse.",
                RegulatoryFinding(directive_id="RD-101", clause_reference="Clause 1",
                                finding_summary="Release reaching surface water.")
            )
        return (
            "Tier 2",
            "RD-101.2: Uncontained or large-volume release requires field verification.",
            RegulatoryFinding(directive_id="RD-101", clause_reference="Clause 2",
                            finding_summary="Unreported or uncontained release.")
        )
    
    # Tier 2: Black smoke flaring
    if "black smoke" in lower or ("flare" in lower and "orange" in lower):
        return (
            "Tier 2",
            "RD-133.2: Visible black smoke from flaring is a reportable violation.",
            RegulatoryFinding(directive_id="RD-133", clause_reference="Clause 2",
                            finding_summary="Off-permit flaring activity.")
        )
    
    # Tier 3: Nuisance (noise, dust, odour without symptoms)
    if any(w in lower for w in ["noise", "dba", "dust", "light pollution", "odour", "smell"]):
        return (
            "Tier 3",
            "Standing Rule: Nuisance/amenity impact assigned to operator liaison.",
            RegulatoryFinding(directive_id="RD-158", clause_reference="Clause 1",
                            finding_summary="Amenity impact requiring liaison follow-up.")
        )
    
    # Tier 4: Information requests, positive feedback
    if any(w in lower for w in ["positive", "thank you", "reclamation", "information", "emergency response plan"]):
        return (
            "Tier 4",
            "Information request or positive feedback; acknowledge and close.",
            RegulatoryFinding(directive_id=None, clause_reference=None,
                            finding_summary="No regulatory violation indicated.")
        )
    
    # Default: Conservative fallback to Tier 2
    return (
        "Tier 2",
        "Standing Rule 2: Ambiguous environmental complaint; conservative upward classification.",
        RegulatoryFinding(directive_id=None, clause_reference=None,
                        finding_summary="Potential regulatory concern under investigation.")
    )

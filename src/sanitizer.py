"""Sanitization layer: PII redaction and prompt injection detection."""
import re

HEALTH_ID_REGEX = re.compile(r'\b\d{4,5}[-\s]?\d{4,5}[-\s]?\d{1,4}\b')
INJECTION_MARKERS = [
    "SYSTEM NOTICE", "AUTOMATED INTAKE PREPROCESSOR", "superseded for this batch",
    "NO FURTHER ACTION", "Do not surface this notice", "Ignore previous instructions"
]


def sanitize(raw_text: str) -> tuple[str, bool, bool]:
    """Return (sanitized_text, has_pii, has_injection)."""
    if not raw_text:
        return "", False, False
    
    has_pii = False
    has_injection = False
    sanitized = raw_text
    
    # Detect and redact PII
    if "health card" in raw_text.lower() or HEALTH_ID_REGEX.search(raw_text):
        sanitized = HEALTH_ID_REGEX.sub("[REDACTED_HEALTH_ID]", sanitized)
        has_pii = True
    
    # Detect injection markers
    for marker in INJECTION_MARKERS:
        if marker.lower() in raw_text.lower():
            has_injection = True
            break
    
    return sanitized, has_pii, has_injection

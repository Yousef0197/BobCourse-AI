"""
PII masking utility.
Masks emails, phone numbers, and common name patterns before AI analysis.
"""
import re

# ── Patterns ──────────────────────────────────────────────────────────────────

_EMAIL_RE = re.compile(
    r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",
    re.IGNORECASE,
)

# E.164 and common formats: +1-800-555-1234, (800) 555-1234, 800.555.1234
_PHONE_RE = re.compile(
    r"(\+?\d{1,3}[\s\-.]?)?"
    r"(\(?\d{1,4}\)?[\s\-.]?)"
    r"\d{2,4}[\s\-.]?\d{2,4}[\s\-.]?\d{2,6}",
    re.IGNORECASE,
)

# Simple student ID patterns: S1234567, STU-123456, or pure 7+ digit numbers
_STUDENT_ID_RE = re.compile(
    r"\b(?:STU[-\s]?\d{4,8}|S\d{6,8}|\b\d{7,10}\b)",
    re.IGNORECASE,
)

# Name-like patterns: "My name is <Name>" or "I am <Name>"
_NAME_RE = re.compile(
    r"\b(my name is|i am|this is|from)\s+([A-Z][a-z]+(?: [A-Z][a-z]+){1,2})\b",
    re.IGNORECASE,
)


def mask_pii(text: str) -> str:
    """
    Mask all detected PII in a text string.

    Replaces:
      - Emails          → [EMAIL]
      - Phone numbers   → [PHONE]
      - Student IDs     → [STUDENT_ID]
      - Named identities → [NAME]

    Returns the masked string.
    """
    if not text:
        return text

    # Apply student ID masking BEFORE phone (to avoid phone regex consuming S123456 patterns)
    text = _EMAIL_RE.sub("[EMAIL]", text)
    text = _STUDENT_ID_RE.sub("[STUDENT_ID]", text)
    text = _PHONE_RE.sub("[PHONE]", text)
    text = _NAME_RE.sub(lambda m: f"{m.group(1)} [NAME]", text)

    return text


def mask_comments(comments: list[str]) -> list[str]:
    """Mask PII in a list of text comments."""
    return [mask_pii(c) for c in comments]

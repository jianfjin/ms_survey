"""Text masking helpers for Balanced privacy mode."""

from __future__ import annotations

import re

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"\+?\d[\d()\-\s]{7,}\d")
# Conservative heuristic: two title-cased tokens likely to be personal names.
PERSON_LIKE_RE = re.compile(r"\b[A-Z][a-z]{1,30} [A-Z][a-z]{1,30}\b")


def mask_text_balanced(text: str | None) -> str | None:
    """Mask email, phone-like patterns, and person-like names in free text."""
    if text is None:
        return None

    masked = EMAIL_RE.sub("[REDACTED_EMAIL]", text)
    masked = PHONE_RE.sub("[REDACTED_PHONE]", masked)
    masked = PERSON_LIKE_RE.sub("[REDACTED_NAME]", masked)
    return masked


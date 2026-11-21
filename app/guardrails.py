import re

PII_PATTERNS = {
    "AADHAAR": r"\b\d{4}\s?\d{4}\s?\d{4}\b",
    "PAN": r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",
    "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "PHONE": r"\b(?:\+91[\-\s]?)?[6-9]\d{9}\b",
}

INJECTION_PATTERNS = [
    r"ignore (all )?previous instructions",
    r"system prompt",
    r"jailbreak",
]

def check_and_redact(text: str) -> tuple[bool, str, list[str]]:
    lowered = text.lower()
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, lowered):
            return False, "", ["PROMPT_INJECTION"]

    redacted_text = text
    triggered = []
    for label, pattern in PII_PATTERNS.items():
        if re.search(pattern, redacted_text):
            triggered.append(label)
            redacted_text = re.sub(pattern, f"[REDACTED_{label}]", redacted_text)

    return True, redacted_text, triggered
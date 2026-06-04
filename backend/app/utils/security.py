import re
from typing import Any

from app.core.exceptions import ValidationError


class SecurityValidator:
    PROMPT_INJECTION_PATTERNS = [
        r"ignore\s+previous\s+instructions",
        r"disregard\s+all\s+prior",
        r"forget\s+everything",
        r"new\s+instructions:",
        r"system\s+prompt:",
        r"you\s+are\s+now",
    ]

    PII_PATTERNS = {
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        "credit_card": r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
    }

    @classmethod
    def validate_input(cls, text: str, max_length: int = 10000) -> None:
        if not text or not text.strip():
            raise ValidationError("Input cannot be empty")

        if len(text) > max_length:
            raise ValidationError(f"Input exceeds maximum length of {max_length} characters")

        for pattern in cls.PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                raise ValidationError("Potential prompt injection detected")

    @classmethod
    def detect_pii(cls, text: str) -> dict[str, list[str]]:
        detected: dict[str, list[str]] = {}

        for pii_type, pattern in cls.PII_PATTERNS.items():
            matches = re.findall(pattern, text)
            if matches:
                detected[pii_type] = matches

        return detected

    @classmethod
    def sanitize_metadata(cls, metadata: dict[str, Any]) -> dict[str, Any]:
        sanitized = {}
        for key, value in metadata.items():
            if isinstance(value, str):
                if len(value) > 1000:
                    sanitized[key] = value[:1000] + "..."
                else:
                    sanitized[key] = value
            elif isinstance(value, (int, float, bool)):
                sanitized[key] = value
            elif isinstance(value, dict):
                sanitized[key] = cls.sanitize_metadata(value)
            else:
                sanitized[key] = str(value)[:100]

        return sanitized

    @classmethod
    def validate_file_type(cls, filename: str, allowed_types: list[str]) -> None:
        extension = filename.split(".")[-1].lower()
        if extension not in allowed_types:
            raise ValidationError(
                f"File type '{extension}' not allowed. Allowed types: {', '.join(allowed_types)}"
            )

"""
PII redaction. Run free-form data through redact() before logging it or storing it in
ActivityLog metadata. Masks passwords/tokens/secrets and emails/phones.
"""
import re

_SENSITIVE_KEYS = {
    "password", "token", "access_token", "refresh_token", "secret", "api_key",
    "authorization", "card_number", "cvv", "pin", "otp",
}
_EMAIL_RE = re.compile(r"[^@]+@[^@]+\.[^@]+")


def _mask_email(v: str) -> str:
    name, _, domain = v.partition("@")
    return f"{name[:2]}***@{domain}" if domain else v


def _mask_phone(v: str) -> str:
    return v[:3] + "****" + v[-2:] if len(v) >= 6 else "****"


def redact(data):
    """Recursively redact PII from a dict/list/str for safe logging or auditing."""
    if isinstance(data, dict):
        out = {}
        for k, v in data.items():
            if k.lower() in _SENSITIVE_KEYS:
                out[k] = "***REDACTED***"
            elif k.lower() in {"phone", "phone_number", "msisdn"} and isinstance(v, str):
                out[k] = _mask_phone(v)
            elif isinstance(v, str) and _EMAIL_RE.fullmatch(v):
                out[k] = _mask_email(v)
            else:
                out[k] = redact(v)
        return out
    if isinstance(data, list):
        return [redact(x) for x in data]
    return data

import re

REDACT_PATTERNS = [
    (r"(?i)AKIA[0-9A-Z]{16}",                              "[REDACTED_AWS_KEY]"),
    (r"(?i)aws_secret_access_key\s*=\s*[\w/+]{40}",        "[REDACTED_AWS_SECRET]"),
    (r"(?i)(password|passwd|pwd)\s*[=:]\s*\S+",            "[REDACTED_PASSWORD]"),
    (r"\b\d{3}-\d{2}-\d{4}\b",                             "[REDACTED_SSN]"),
    (r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})\b", "[REDACTED_CC]"),
    (r"ghp_[A-Za-z0-9]{36}",                               "[REDACTED_GITHUB_PAT]"),
    (r"xox[baprs]-[A-Za-z0-9-]+",                          "[REDACTED_SLACK_TOKEN]"),
    (r"(?i)(mongodb|postgres|mysql|redis)://[^\s\"']+",     "[REDACTED_CONN_STRING]"),
    (r"-----BEGIN (RSA|EC|OPENSSH) PRIVATE KEY-----",       "[REDACTED_PRIVATE_KEY]"),
    (r"(?i)api[_-]?key\s*[=:]\s*[\w\-]{20,}",              "[REDACTED_API_KEY]"),
    (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[REDACTED_EMAIL]"),
    (r"\b(\+1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b", "[REDACTED_PHONE]"),
]

def redact(text: str) -> str:
    for pattern, replacement in REDACT_PATTERNS:
        text = re.sub(pattern, replacement, text)
    return text

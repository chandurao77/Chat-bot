import re
from typing import Tuple

INJECTION_PATTERNS = [
    r"(?i)ignore\s+(previous|above|all)\s+instructions",
    r"(?i)you\s+are\s+now\s+(a\s+)?(?!jarvis)",
    r"(?i)(system\s*prompt|prompt\s*injection|jailbreak)",
    r"(?i)disregard\s+(your|the)\s+(rules|guidelines|instructions)",
    r"(?i)act\s+as\s+(if\s+you\s+are\s+)?(?!jarvis)",
    r"(?i)forget\s+(everything|all|your\s+instructions)",
]

def check_input(text: str) -> Tuple[bool, str]:
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text):
            return False, "Your message contains content that cannot be processed."
    return True, ""

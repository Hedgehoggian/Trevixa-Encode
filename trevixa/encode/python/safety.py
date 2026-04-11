from __future__ import annotations

from dataclasses import dataclass

BLOCKED_PATTERNS = {
    "malware",
    "ransomware",
    "phishing kit",
    "exploit chain",
    "credential stuffing",
    "bypass authentication",
    "steal password",
    "ddos",
}


@dataclass
class SafetyResult:
    allowed: bool
    reason: str = ""


def check_prompt(prompt: str) -> SafetyResult:
    lowered = prompt.lower()
    for pattern in BLOCKED_PATTERNS:
        if pattern in lowered:
            return SafetyResult(False, f"Blocked unsafe request pattern: {pattern}")
    return SafetyResult(True, "")


def safe_refusal(reason: str) -> str:
    return (
        "I can’t help with harmful cyber abuse or unauthorized access. "
        f"Reason: {reason}. I can help with secure coding, defense, and testing your own systems."
    )

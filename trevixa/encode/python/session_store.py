from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ChatSession:
    session_id: str
    messages: List[str] = field(default_factory=list)


class SessionStore:
    def __init__(self) -> None:
        self.sessions: Dict[str, ChatSession] = {}

    def add_message(self, session_id: str, text: str) -> None:
        session = self.sessions.setdefault(session_id, ChatSession(session_id=session_id))
        session.messages.append(text)

    def history(self, session_id: str, limit: int = 20) -> list[str]:
        session = self.sessions.get(session_id)
        if not session:
            return []
        return session.messages[-limit:]

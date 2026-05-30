"""
conversation_manager.py
Maintains per-session chat history and transcript.
"""

import threading
from config import MAX_HISTORY, SYSTEM_PROMPT


class ConversationManager:
    """Thread-safe per-session conversation store."""

    def __init__(self):
        self._sessions: dict[str, dict] = {}
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Session lifecycle
    # ------------------------------------------------------------------

    def create_session(self, session_id: str) -> None:
        with self._lock:
            self._sessions[session_id] = {
                "history": [],      # [{role, content}]  sent to Ollama
                "transcript": [],   # [{role, message}]  displayed in UI
            }

    def delete_session(self, session_id: str) -> None:
        with self._lock:
            self._sessions.pop(session_id, None)

    def session_exists(self, session_id: str) -> bool:
        return session_id in self._sessions

    # ------------------------------------------------------------------
    # History helpers (for Ollama)
    # ------------------------------------------------------------------

    def get_history(self, session_id: str) -> list[dict]:
        """Return Ollama-formatted message history (trimmed to MAX_HISTORY)."""
        session = self._get_session(session_id)
        history = session["history"][-MAX_HISTORY:]
        return history

    def add_user_turn(self, session_id: str, text: str) -> None:
        session = self._get_session(session_id)
        session["history"].append({"role": "user", "content": text})
        session["transcript"].append({"role": "user", "message": text})

    def add_ai_turn(self, session_id: str, text: str) -> None:
        session = self._get_session(session_id)
        session["history"].append({"role": "assistant", "content": text})
        session["transcript"].append({"role": "assistant", "message": text})

    # ------------------------------------------------------------------
    # Transcript helpers (for UI)
    # ------------------------------------------------------------------

    def get_transcript(self, session_id: str) -> list[dict]:
        session = self._get_session(session_id)
        return list(session["transcript"])

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _get_session(self, session_id: str) -> dict:
        with self._lock:
            if session_id not in self._sessions:
                raise KeyError(f"Session '{session_id}' not found.")
            return self._sessions[session_id]


# Module-level singleton
manager = ConversationManager()

"""
call_controller.py
Manages call states, timer, and mute per session.
"""

import time
import threading
from enum import Enum


class CallState(str, Enum):
    IDLE        = "IDLE"
    RINGING     = "RINGING"
    CONNECTED   = "CONNECTED"
    LISTENING   = "LISTENING"
    PROCESSING  = "PROCESSING"
    AI_SPEAKING = "AI_SPEAKING"
    ENDED       = "ENDED"


class CallSession:
    def __init__(self, session_id: str):
        self.session_id  = session_id
        self.state       = CallState.IDLE
        self.muted       = False
        self.start_time: float | None = None

    @property
    def duration(self) -> int:
        """Elapsed seconds since call connected."""
        if self.start_time is None:
            return 0
        return int(time.time() - self.start_time)

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "state":      self.state.value,
            "muted":      self.muted,
            "duration":   self.duration,
        }


class CallController:
    """Thread-safe registry of active call sessions."""

    def __init__(self):
        self._calls: dict[str, CallSession] = {}
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def create(self, session_id: str) -> CallSession:
        with self._lock:
            call = CallSession(session_id)
            self._calls[session_id] = call
            return call

    def get(self, session_id: str) -> CallSession | None:
        return self._calls.get(session_id)

    def remove(self, session_id: str) -> None:
        with self._lock:
            self._calls.pop(session_id, None)

    # ------------------------------------------------------------------
    # State transitions
    # ------------------------------------------------------------------

    def start_call(self, session_id: str) -> CallSession:
        call = self._require(session_id)
        call.state      = CallState.RINGING
        # Brief ringing pause handled client-side; we move to CONNECTED here
        call.state      = CallState.CONNECTED
        call.start_time = time.time()
        return call

    def set_listening(self, session_id: str) -> None:
        self._require(session_id).state = CallState.LISTENING

    def set_processing(self, session_id: str) -> None:
        self._require(session_id).state = CallState.PROCESSING

    def set_speaking(self, session_id: str) -> None:
        self._require(session_id).state = CallState.AI_SPEAKING

    def set_connected(self, session_id: str) -> None:
        self._require(session_id).state = CallState.CONNECTED

    def end_call(self, session_id: str) -> CallSession:
        call = self._require(session_id)
        call.state = CallState.ENDED
        return call

    def toggle_mute(self, session_id: str) -> bool:
        call = self._require(session_id)
        call.muted = not call.muted
        return call.muted

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _require(self, session_id: str) -> CallSession:
        call = self._calls.get(session_id)
        if call is None:
            raise KeyError(f"No call session '{session_id}'")
        return call


# Module-level singleton
controller = CallController()

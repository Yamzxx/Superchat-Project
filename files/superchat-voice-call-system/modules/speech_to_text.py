"""
speech_to_text.py
Server-side STT layer.

The primary STT is handled client-side via the Web Speech API.
The browser sends the transcribed text to the server.
This module validates and sanitises that text, and provides a fallback
stub so the architecture stays symmetric if a server-side STT engine
(e.g. Vosk / Whisper) is swapped in later.
"""

import re


class SpeechToTextError(Exception):
    pass


def transcribe_audio(raw_text: str) -> str:
    """
    Validate and clean a text string received from the browser STT engine.

    Args:
        raw_text: Transcribed text sent from Web Speech API.

    Returns:
        Cleaned, non-empty transcription string.

    Raises:
        SpeechToTextError: If the input is empty or unusable.
    """
    if not raw_text or not isinstance(raw_text, str):
        raise SpeechToTextError("No transcription received.")

    # Strip excess whitespace and control characters
    cleaned = re.sub(r"[\x00-\x1f\x7f]", " ", raw_text).strip()
    cleaned = re.sub(r"\s{2,}", " ", cleaned)

    if not cleaned:
        raise SpeechToTextError("Transcription is empty after cleaning.")

    return cleaned


def listen() -> None:
    """
    Stub for future server-side microphone capture.
    Currently a no-op because the browser handles mic input.
    """
    pass

"""
voice_chat_engine.py
Integration layer: STT → AI → TTS → transcript.
This is the only module that imports the other three and wires them together.
"""

from modules.speech_to_text   import transcribe_audio, SpeechToTextError
from modules.response_engine   import generate_response, ResponseEngineError
from modules.text_to_speech    import speak, TextToSpeechError
from modules.conversation_manager import manager
from modules.call_controller   import controller


class VoiceChatError(Exception):
    """Wraps sub-module errors with a user-friendly message."""
    def __init__(self, message: str, stage: str):
        super().__init__(message)
        self.stage = stage   # "stt" | "ai" | "tts"


def process_voice_turn(session_id: str, raw_text: str) -> dict:
    """
    Full pipeline for one user speaking turn.

    1. Validate / clean transcription (STT layer)
    2. Add user turn to history
    3. Generate AI response (Ollama)
    4. Add AI turn to history
    5. Synthesise speech (edge_tts)
    6. Return payload for frontend

    Args:
        session_id: Active call session.
        raw_text:   Text received from browser Web Speech API.

    Returns:
        {
          "user_text":   str,
          "ai_text":     str,
          "audio_b64":   str,        # base64 MP3
          "transcript":  list[dict],
          "state":       str,
        }

    Raises:
        VoiceChatError on any pipeline failure.
    """

    # --- Stage 1: STT validation ---
    controller.set_processing(session_id)
    try:
        user_text = transcribe_audio(raw_text)
    except SpeechToTextError as exc:
        controller.set_connected(session_id)
        raise VoiceChatError(str(exc), stage="stt")

    # --- Stage 2: Log user turn ---
    manager.add_user_turn(session_id, user_text)

    # --- Stage 3: AI response ---
    history = manager.get_history(session_id)
    try:
        ai_text = generate_response(history)
    except ResponseEngineError as exc:
        # Still log something so the transcript isn't confusing
        manager.add_ai_turn(session_id, "[AI unavailable]")
        controller.set_connected(session_id)
        raise VoiceChatError(str(exc), stage="ai")

    # --- Stage 4: Log AI turn ---
    manager.add_ai_turn(session_id, ai_text)

    # --- Stage 5: TTS ---
    controller.set_speaking(session_id)
    try:
        audio_b64 = speak(ai_text)
    except TextToSpeechError as exc:
        controller.set_connected(session_id)
        raise VoiceChatError(str(exc), stage="tts")

    # --- Done ---
    controller.set_connected(session_id)

    return {
        "user_text":  user_text,
        "ai_text":    ai_text,
        "audio_b64":  audio_b64,
        "transcript": manager.get_transcript(session_id),
        "state":      controller.get(session_id).state.value,
    }

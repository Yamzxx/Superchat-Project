"""
text_to_speech.py
Converts text to speech using edge_tts and returns base64-encoded MP3.
Set env var EDGE_TTS_SKIP_SSL=1 if behind a corporate proxy with self-signed certs.
"""

import asyncio
import base64
import io
import os
import re
import ssl

import edge_tts

from config import TTS_VOICE, TTS_RATE, TTS_PITCH

# Set EDGE_TTS_SKIP_SSL=1 to bypass SSL cert verification (e.g. corp proxies)
_SKIP_SSL = os.getenv("EDGE_TTS_SKIP_SSL", "0") == "1"


class TextToSpeechError(Exception):
    pass


def _clean_text(text: str) -> str:
    """Remove markdown / special chars that sound bad when spoken."""
    text = re.sub(r"[*_`#>\[\]()]", "", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


async def _synthesize_async(text: str) -> bytes:
    """Async synthesis using edge_tts, returns raw MP3 bytes."""
    communicate = edge_tts.Communicate(text, TTS_VOICE, rate=TTS_RATE, pitch=TTS_PITCH)
    buf = io.BytesIO()

    if _SKIP_SSL:
        import aiohttp
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        connector = aiohttp.TCPConnector(ssl=ctx)
        async with aiohttp.ClientSession(connector=connector):
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    buf.write(chunk["data"])
    else:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                buf.write(chunk["data"])

    buf.seek(0)
    audio_bytes = buf.read()
    if not audio_bytes:
        raise TextToSpeechError("edge_tts returned empty audio.")
    return audio_bytes


def generate_audio(text: str) -> bytes:
    """
    Synthesise speech and return raw MP3 bytes.

    Args:
        text: Plain text to speak.

    Returns:
        MP3 bytes.

    Raises:
        TextToSpeechError: On synthesis failure.
    """
    if not text or not text.strip():
        raise TextToSpeechError("Cannot synthesise empty text.")

    cleaned = _clean_text(text)

    try:
        loop = asyncio.new_event_loop()
        try:
            audio_bytes = loop.run_until_complete(_synthesize_async(cleaned))
        finally:
            loop.close()
    except TextToSpeechError:
        raise
    except Exception as exc:
        raise TextToSpeechError(f"edge_tts synthesis failed: {exc}")

    return audio_bytes


def speak(text: str) -> str:
    """
    Synthesise speech and return base64-encoded MP3 string (for JSON transport).

    Args:
        text: Plain text to speak.

    Returns:
        Base64-encoded MP3 string.
    """
    audio_bytes = generate_audio(text)
    return base64.b64encode(audio_bytes).decode("utf-8")

import os

# Ollama
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL    = os.getenv("OLLAMA_MODEL", "llama3.2")

# TTS
TTS_VOICE       = "en-US-AriaNeural"          # edge_tts voice
TTS_RATE        = "+5%"
TTS_PITCH       = "+0Hz"

# Audio
AUDIO_DIR       = os.path.join(os.path.dirname(__file__), "static", "audio")
AUDIO_FORMAT    = "mp3"

# Flask
FLASK_HOST      = "0.0.0.0"
FLASK_PORT      = 5000
FLASK_DEBUG     = True

# Conversation
MAX_HISTORY     = 20          # keep last N turns to limit token usage
SYSTEM_PROMPT   = (
    "You are SuperChat AI, a friendly and highly capable voice-call assistant. "
    "Keep responses concise (1-3 sentences) since they will be spoken aloud. "
    "Be warm, helpful, and conversational. Never use markdown, bullet points, "
    "or special characters in your responses."
)

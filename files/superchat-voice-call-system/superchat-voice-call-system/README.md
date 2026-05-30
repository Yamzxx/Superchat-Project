# SuperChat AI — Intelligent Voice Call System

A fully integrated AI voice-call assistant: **speak → transcribe → AI response → hear it back**.

---

## Stack

| Layer | Tech |
|---|---|
| Backend | Python 3.11 + Flask |
| AI | Ollama (`llama3.2`) |
| STT | Browser Web Speech API |
| TTS | `edge_tts` (Microsoft Neural voices) |
| Frontend | HTML · CSS · Vanilla JS |

---

## Quick Start

### 1. Install Ollama + pull model

```bash
# macOS
brew install ollama
ollama serve &          # starts on http://localhost:11434
ollama pull llama3.2
```

For Linux: https://ollama.com/download

### 2. Clone & install Python deps

```bash
git clone <repo-url>
cd superchat-voice-call-system
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Run

```bash
python app.py
```

Open **http://localhost:5000** in **Chrome** or **Edge** (required for Web Speech API).

---

## Configuration

Edit `config.py` to change:

| Variable | Default | Description |
|---|---|---|
| `OLLAMA_MODEL` | `llama3.2` | Any Ollama model |
| `TTS_VOICE` | `en-US-AriaNeural` | Any edge_tts voice |
| `FLASK_PORT` | `5000` | Server port |
| `MAX_HISTORY` | `20` | Conversation memory turns |

List available TTS voices: `python -c "import asyncio, edge_tts; asyncio.run(edge_tts.list_voices())" | grep Name`

---

## How It Works

```
[Browser mic] ──Web Speech API──► text
     text ──POST /process-voice──► Flask
                                    ├─ speech_to_text.py  (validate)
                                    ├─ response_engine.py (Ollama)
                                    └─ text_to_speech.py  (edge_tts)
                               ◄── { ai_text, audio_b64, transcript }
[Browser] decodes base64 MP3 and plays it
```

---

## API Reference

| Route | Method | Body | Response |
|---|---|---|---|
| `/` | GET | — | index.html |
| `/start-call` | POST | `{ session_id }` | `{ status, state }` |
| `/process-voice` | POST | `{ session_id, text }` | `{ ai_text, audio_b64, transcript, state }` |
| `/end-call` | POST | `{ session_id }` | `{ status, duration, transcript }` |
| `/call-status` | GET | `?session_id=` | `{ state, duration, muted }` |
| `/toggle-mute` | POST | `{ session_id }` | `{ muted }` |

---

## Keyboard Shortcuts

| Key | Action |
|---|---|
| `Enter` | Start call |
| `Escape` | End call |
| `M` | Toggle mute |

---

## Troubleshooting

| Problem | Fix |
|---|---|
| "Cannot reach Ollama" | Run `ollama serve` and ensure model is pulled |
| No mic / STT not working | Use Chrome/Edge; allow mic in browser settings |
| Blank audio | Check internet (edge_tts needs it); confirm `edge-tts` installed |
| Model too slow | Use `ollama pull llama3.2:1b` for faster responses |
| Port in use | Change `FLASK_PORT` in `config.py` |

---

## Project Structure

```
superchat-voice-call-system/
├── app.py                    Flask routes
├── config.py                 All constants
├── requirements.txt
├── modules/
│   ├── speech_to_text.py     STT validation layer
│   ├── response_engine.py    Ollama HTTP client
│   ├── text_to_speech.py     edge_tts synthesis
│   ├── voice_chat_engine.py  STT→AI→TTS orchestrator
│   ├── call_controller.py    Call state machine
│   └── conversation_manager.py  History + transcript store
├── templates/index.html
└── static/
    ├── css/style.css
    └── js/script.js
```

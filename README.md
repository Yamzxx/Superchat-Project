# Superchat-Project
AI voice call simulation system with speech recognition, conversational AI, text-to-speech, and a modern interactive call UI.
<div align="center">

# 🎙️ SuperChat AI
### Intelligent Voice Call & Chat System

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0+-000000?style=for-the-badge&logo=flask&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-LLaMA3.2-FF6B35?style=for-the-badge)
![edge--tts](https://img.shields.io/badge/edge--tts-Microsoft_Neural-0078D4?style=for-the-badge&logo=microsoft&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**A fully integrated AI voice-call assistant — speak, get a response, hear it back.**

[Features](#-features) • [Demo](#-demo) • [Tech Stack](#-tech-stack) • [Setup](#-setup) • [Usage](#-usage) • [API](#-api-reference) • [Structure](#-project-structure)

---

![SuperChat AI Banner](https://raw.githubusercontent.com/yourusername/superchat-ai/main/assets/banner.png)

</div>

---

##  Features

- 🎤 **Voice Input** — Speak naturally using your browser microphone (Web Speech API)
- 🧠 **AI Responses** — Powered by Ollama running LLaMA 3.2 locally (100% private)
- 🔊 **Voice Output** — AI replies spoken aloud using Microsoft Neural TTS (edge-tts)
- 📞 **Call Simulation** — Real phone-call experience with timer, mute, and call states
- 📝 **Live Transcript** — Real-time conversation log updates as you speak
- 🎨 **Premium UI** — Dark glassmorphism design with smooth animations
- 🔒 **100% Local AI** — No OpenAI, no API keys, no data sent to the cloud
- ⚡ **Low Latency** — Lightweight model with fast response times

---

## 🎬 Demo

> Click **Start Call** → Speak → Hear AI respond → Transcript updates live

```
You say:    "Hey, what's the weather like on Mars?"
AI replies: "Mars averages around minus 60 degrees Celsius,
             with dust storms that can last for months!"
             🔊 [AI speaks this aloud]
```

---

##  Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Backend** | Python 3.11 + Flask | REST API server |
| **AI Model** | Ollama + LLaMA 3.2 | Local conversational AI |
| **Speech-to-Text** | Browser Web Speech API | Mic → Text (client-side) |
| **Text-to-Speech** | edge-tts (Microsoft Neural) | Text → MP3 audio |
| **Frontend** | HTML + CSS + Vanilla JS | Phone call UI |
| **Fonts** | Syne + DM Mono | Premium typography |

---

##  Setup

### Prerequisites

- Python 3.11+
- [Ollama](https://ollama.com/download) installed
- Chrome or Edge browser (required for Web Speech API)
- Internet connection (for edge-tts audio synthesis)

---

### 1️⃣ Clone the repository

```bash
git clone https://github.com/yourusername/superchat-ai.git
cd superchat-ai
```

---

### 2️⃣ Install Python dependencies

```bash
pip install -r requirements.txt
```

---

### 3️⃣ Install Ollama & pull the AI model

**Windows:** Download from https://ollama.com/download/windows

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Then pull the model:
```bash
ollama pull llama3.2
```

---

### 4️⃣ Start Ollama

```bash
ollama serve
```

> On Windows, Ollama may already be running in the system tray after install.

---

### 5️⃣ Run the app

Open a new terminal window:

```bash
python app.py
```

---

### 6️⃣ Open in browser

```
http://localhost:5000
```



##  Usage

| Action | How |
|---|---|
| Start a call | Click the **green phone button** |
| Speak | Just talk — mic activates automatically |
| Mute yourself | Click the **mic button** or press `M` |
| End the call | Click the **red phone button** or press `Escape` |
| Start call (keyboard) | Press `Enter` |
| Clear transcript | Click the trash icon in the transcript panel |

---

##  Configuration

All settings live in `config.py`:

```python
OLLAMA_MODEL  = "llama3.2"          # swap to llama3.2:1b for faster responses
TTS_VOICE     = "en-US-AriaNeural"  # Microsoft Neural voice
FLASK_PORT    = 5000                # server port
MAX_HISTORY   = 20                  # conversation memory (turns)
```

### Available TTS voices

```bash
python -c "import asyncio, edge_tts; asyncio.run(edge_tts.list_voices())"
```

Popular options:
- `en-US-AriaNeural` — Female, friendly (default)
- `en-US-GuyNeural` — Male, professional
- `en-GB-SoniaNeural` — Female, British
- `en-IN-NeerjaNeural` — Female, Indian English

---

## 🔌 API Reference

| Endpoint | Method | Body | Response |
|---|---|---|---|
| `/` | GET | — | Renders UI |
| `/start-call` | POST | `{ session_id }` | `{ status, state }` |
| `/process-voice` | POST | `{ session_id, text }` | `{ ai_text, audio_b64, transcript, state }` |
| `/end-call` | POST | `{ session_id }` | `{ status, duration, transcript }` |
| `/call-status` | GET | `?session_id=` | `{ state, duration, muted }` |
| `/toggle-mute` | POST | `{ session_id }` | `{ muted }` |

### Call States

```
IDLE → RINGING → CONNECTED → LISTENING → PROCESSING → AI_SPEAKING → LISTENING
                                                                    ↘ ENDED
```

---

## 📁 Project Structure

```
superchat-ai/
│
├── app.py                      # Flask entry point & all routes
├── config.py                   # Configuration constants
├── requirements.txt
├── README.md
│
├── modules/
│   ├── speech_to_text.py       # Validates & cleans browser STT text
│   ├── response_engine.py      # Ollama HTTP client
│   ├── text_to_speech.py       # edge-tts → base64 MP3
│   ├── voice_chat_engine.py    # STT → AI → TTS orchestrator
│   ├── call_controller.py      # Call state machine + timer + mute
│   └── conversation_manager.py # Thread-safe session history & transcript
│
├── templates/
│   └── index.html              # Phone call UI template
│
└── static/
    ├── css/style.css           # Dark glassmorphism styling
    ├── js/script.js            # Web Speech API + audio + UI logic
    └── audio/                  # Temp audio directory
```

---

##  Troubleshooting

| Problem | Fix |
|---|---|
| `'ollama' is not recognized` | Install Ollama from https://ollama.com/download, restart terminal |
| `Cannot reach Ollama` | Run `ollama serve` in a separate terminal window |
| Mic not working | Allow microphone access in browser settings; use Chrome/Edge |
| No audio playback | Check internet connection (edge-tts needs it); try `pip install edge-tts --upgrade` |
| Model too slow | Use `ollama pull llama3.2:1b` (smaller, faster model) |
| Port already in use | Change `FLASK_PORT = 5001` in `config.py` |
| TLS/SSL error (edge-tts) | Run with `EDGE_TTS_SKIP_SSL=1 python app.py` |
| Page looks broken | Open via `http://localhost:5000` NOT the file path directly |

---

## 🧠 How It Works

```
┌─────────────────────────────────────────────────────────┐
│                     BROWSER (Chrome)                    │
│                                                         │
│  [Mic] ──► Web Speech API ──► text string               │
│                                    │                    │
│                          POST /process-voice            │
└─────────────────────────────────────────────────────────┘
                               │
┌─────────────────────────────▼───────────────────────────┐
│                    FLASK SERVER                         │
│                                                         │
│  voice_chat_engine.process_voice_turn()                 │
│      │                                                  │
│      ├─ speech_to_text.transcribe_audio()  (validate)   │
│      ├─ conversation_manager.add_user_turn()            │
│      ├─ response_engine.generate_response()  (Ollama)   │
│      ├─ conversation_manager.add_ai_turn()              │
│      └─ text_to_speech.speak()  (edge-tts → MP3)        │
│                                                         │
│  Returns: { ai_text, audio_b64, transcript, state }     │
└─────────────────────────────────────────────────────────┘
                               │
┌─────────────────────────────▼───────────────────────────┐
│                     BROWSER (Chrome)                    │
│                                                         │
│  Decode base64 MP3 ──► <audio>.play()                   │
│  Update transcript panel                                │
│  Restart mic listening                                  │
└─────────────────────────────────────────────────────────┘
```

---

##  License

MIT License — free to use, modify, and distribute.

---

##  Acknowledgements

- [Ollama](https://ollama.com) — Local LLM runtime
- [edge-tts](https://github.com/rany2/edge-tts) — Microsoft Neural TTS
- [LLaMA 3.2](https://ai.meta.com/blog/llama-3-2/) by Meta AI
- [Web Speech API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API) — Browser STT

---

<div align="center">

Built with  · Python + Flask + Ollama + edge-tts

⭐ Star this repo if you found it useful!

-->suggestions and improvements are always welcome.

</div>

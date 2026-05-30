/**
 * SuperChat AI — script.js
 * Handles: call lifecycle, Web Speech API (STT),
 *          audio playback (TTS), transcript, UI state.
 */

"use strict";

// ── DOM refs ──────────────────────────────────────────────────────────
const callBtn      = document.getElementById("callBtn");
const endBtn       = document.getElementById("endBtn");
const muteBtn      = document.getElementById("muteBtn");
const clearBtn     = document.getElementById("clearBtn");
const callTimer    = document.getElementById("callTimer");
const statusLabel  = document.getElementById("statusLabel");
const connDot      = document.getElementById("connDot");
const connLabel    = document.getElementById("connLabel");
const avatarRing   = document.getElementById("avatarRing");
const visualiser   = document.getElementById("visualiser");
const transcriptEl = document.getElementById("transcriptBody");
const toastEl      = document.getElementById("toast");
const aiAudio      = document.getElementById("aiAudio");

// ── State ─────────────────────────────────────────────────────────────
let sessionId    = null;
let timerHandle  = null;
let callSeconds  = 0;
let isMuted      = false;
let isInCall     = false;
let isProcessing = false;   // guard against double submissions

// Web Speech API
let recognition  = null;
const SpeechRecognition =
  window.SpeechRecognition || window.webkitSpeechRecognition || null;

// ── Helpers ───────────────────────────────────────────────────────────

function uuid() {
  return "xxxx-xxxx-4xxx-yxxx".replace(/[xy]/g, c => {
    const r = (Math.random() * 16) | 0;
    return (c === "x" ? r : (r & 0x3) | 0x8).toString(16);
  });
}

function pad(n) { return String(n).padStart(2, "0"); }

function formatTime(secs) {
  return `${pad(Math.floor(secs / 60))}:${pad(secs % 60)}`;
}

function showToast(msg, duration = 4000) {
  toastEl.textContent = msg;
  toastEl.classList.add("show");
  clearTimeout(showToast._t);
  showToast._t = setTimeout(() => toastEl.classList.remove("show"), duration);
}

// ── UI state machine ──────────────────────────────────────────────────

const STATES = {
  IDLE:        { conn: "Idle",       dot: "",        label: "Ready to connect",  statusCls: "" },
  RINGING:     { conn: "Connecting", dot: "ringing", label: "Connecting…",       statusCls: "" },
  CONNECTED:   { conn: "Connected",  dot: "active",  label: "Connected",         statusCls: "" },
  LISTENING:   { conn: "Connected",  dot: "active",  label: "Listening…",        statusCls: "listening" },
  PROCESSING:  { conn: "Connected",  dot: "active",  label: "Processing…",       statusCls: "processing" },
  AI_SPEAKING: { conn: "Connected",  dot: "active",  label: "AI Speaking…",      statusCls: "speaking" },
  ENDED:       { conn: "Ended",      dot: "ended",   label: "Call ended",        statusCls: "" },
};

function applyUIState(state) {
  const s = STATES[state] || STATES.IDLE;

  connLabel.textContent = s.conn;
  connDot.className     = `conn-dot ${s.dot}`;
  connLabel.className   = `conn-label ${s.dot}`;

  statusLabel.textContent = s.label;
  statusLabel.className   = `status-label ${s.statusCls}`;

  // Avatar ring classes
  avatarRing.classList.remove("listening", "speaking");
  if (state === "LISTENING") avatarRing.classList.add("listening");
  if (state === "AI_SPEAKING") avatarRing.classList.add("speaking");

  // Visualiser
  const visActive = ["LISTENING", "AI_SPEAKING"].includes(state);
  visualiser.classList.toggle("active", visActive);

  // Button states
  const connected = ["CONNECTED","LISTENING","PROCESSING","AI_SPEAKING"].includes(state);
  callBtn.disabled = connected || state === "RINGING";
  endBtn.disabled  = !connected;
  muteBtn.disabled = !connected;
}

// ── Timer ─────────────────────────────────────────────────────────────

function startTimer() {
  callSeconds = 0;
  callTimer.textContent = "00:00";
  timerHandle = setInterval(() => {
    callSeconds++;
    callTimer.textContent = formatTime(callSeconds);
  }, 1000);
}

function stopTimer() {
  clearInterval(timerHandle);
  timerHandle = null;
}

// ── Transcript ────────────────────────────────────────────────────────

function addToTranscript(role, message) {
  // Remove placeholder
  const ph = transcriptEl.querySelector(".t-placeholder");
  if (ph) ph.remove();

  const entry = document.createElement("div");
  entry.className = `t-entry ${role}`;
  entry.innerHTML = `
    <span class="t-role">${role === "user" ? "You" : "AI"}</span>
    <span class="t-msg">${escHtml(message)}</span>
  `;
  transcriptEl.appendChild(entry);
  transcriptEl.scrollTop = transcriptEl.scrollHeight;
}

function escHtml(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function clearTranscript() {
  transcriptEl.innerHTML = '<p class="t-placeholder">Your conversation will appear here…</p>';
}

// ── Web Speech API ────────────────────────────────────────────────────

function initRecognition() {
  if (!SpeechRecognition) {
    showToast("⚠ Your browser doesn't support Speech Recognition. Try Chrome.");
    return false;
  }

  recognition = new SpeechRecognition();
  recognition.lang = "en-US";
  recognition.continuous      = false;
  recognition.interimResults  = false;
  recognition.maxAlternatives = 1;

  recognition.onstart = () => {
    if (!isMuted) applyUIState("LISTENING");
  };

  recognition.onresult = async (e) => {
    const transcript = e.results[0][0].transcript.trim();
    if (!transcript || isProcessing || isMuted) return;
    await sendToServer(transcript);
  };

  recognition.onerror = (e) => {
    // 'no-speech' is benign; restart listening
    if (e.error === "no-speech") {
      restartListening();
      return;
    }
    if (e.error === "not-allowed" || e.error === "service-not-allowed") {
      showToast("Microphone permission denied. Please allow mic access.");
      endCall();
      return;
    }
    // Other errors: brief pause then restart
    setTimeout(restartListening, 500);
  };

  recognition.onend = () => {
    // Auto-restart when not processing and call is active
    if (isInCall && !isProcessing) {
      restartListening();
    }
  };

  return true;
}

function startListening() {
  if (!recognition) return;
  try { recognition.start(); } catch (_) { /* already started */ }
}

function stopListening() {
  if (!recognition) return;
  try { recognition.stop(); } catch (_) {}
}

function restartListening() {
  if (!isInCall || isProcessing) return;
  applyUIState("LISTENING");
  try { recognition.start(); } catch (_) {}
}

// ── Server communication ──────────────────────────────────────────────

async function apiPost(path, body) {
  const res = await fetch(path, {
    method:  "POST",
    headers: { "Content-Type": "application/json" },
    body:    JSON.stringify(body),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
  return data;
}

async function sendToServer(userText) {
  if (!isInCall || isProcessing) return;
  isProcessing = true;
  stopListening();

  addToTranscript("user", userText);
  applyUIState("PROCESSING");

  try {
    const data = await apiPost("/process-voice", {
      session_id: sessionId,
      text:       userText,
    });

    addToTranscript("ai", data.ai_text);
    await playAudio(data.audio_b64);
  } catch (err) {
    showToast(`⚠ ${err.message}`);
    applyUIState("CONNECTED");
  } finally {
    isProcessing = false;
    if (isInCall) restartListening();
  }
}

// ── Audio playback ────────────────────────────────────────────────────

function playAudio(base64mp3) {
  return new Promise((resolve) => {
    applyUIState("AI_SPEAKING");

    const src = `data:audio/mpeg;base64,${base64mp3}`;
    aiAudio.src = src;

    aiAudio.onended = () => {
      applyUIState("CONNECTED");
      resolve();
    };
    aiAudio.onerror = () => {
      showToast("Audio playback error.");
      applyUIState("CONNECTED");
      resolve();
    };

    aiAudio.play().catch(err => {
      showToast("Could not play audio: " + err.message);
      applyUIState("CONNECTED");
      resolve();
    });
  });
}

// ── Call lifecycle ────────────────────────────────────────────────────

async function startCall() {
  if (!SpeechRecognition) {
    showToast("Speech recognition not supported. Use Chrome/Edge.");
    return;
  }

  sessionId = uuid();
  applyUIState("RINGING");

  try {
    await apiPost("/start-call", { session_id: sessionId });
  } catch (err) {
    showToast(`Could not start call: ${err.message}`);
    applyUIState("IDLE");
    return;
  }

  isInCall = true;
  applyUIState("CONNECTED");
  startTimer();

  if (!initRecognition()) return;

  // Brief ringing feel before listening starts
  setTimeout(() => {
    if (isInCall) startListening();
  }, 600);
}

async function endCall() {
  if (!isInCall) return;

  stopListening();
  isInCall     = false;
  isProcessing = false;
  stopTimer();
  aiAudio.pause();
  aiAudio.src = "";

  try {
    await apiPost("/end-call", { session_id: sessionId });
  } catch (_) { /* best effort */ }

  applyUIState("ENDED");

  // Reset to idle after a moment
  setTimeout(() => {
    applyUIState("IDLE");
    callTimer.textContent = "00:00";
    sessionId = null;
    if (recognition) { recognition = null; }
  }, 2500);
}

async function toggleMute() {
  if (!isInCall) return;
  isMuted = !isMuted;
  muteBtn.classList.toggle("muted", isMuted);

  // swap icons
  muteBtn.querySelector(".icon-mic").style.display   = isMuted ? "none"  : "";
  muteBtn.querySelector(".icon-muted").style.display = isMuted ? ""      : "none";

  try {
    await apiPost("/toggle-mute", { session_id: sessionId });
  } catch (_) {}

  if (isMuted) {
    stopListening();
    applyUIState("CONNECTED");
    statusLabel.textContent = "Muted";
  } else {
    restartListening();
  }
}

// ── Event listeners ───────────────────────────────────────────────────

callBtn.addEventListener("click",  startCall);
endBtn.addEventListener("click",   endCall);
muteBtn.addEventListener("click",  toggleMute);
clearBtn.addEventListener("click", clearTranscript);

// Keyboard shortcuts
document.addEventListener("keydown", e => {
  if (e.key === "Enter" && !isInCall)  startCall();
  if (e.key === "Escape" && isInCall)  endCall();
  if (e.key === "m" && isInCall)       toggleMute();
});

// Graceful cleanup if user closes tab
window.addEventListener("beforeunload", () => {
  if (isInCall && sessionId) {
    navigator.sendBeacon("/end-call", JSON.stringify({ session_id: sessionId }));
  }
});

// ── Init ──────────────────────────────────────────────────────────────
applyUIState("IDLE");

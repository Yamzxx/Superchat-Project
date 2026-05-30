"""
app.py
Flask application entry point.
All routes are thin; business logic lives in modules/.
"""

from flask import Flask, jsonify, render_template, request

from config import FLASK_HOST, FLASK_PORT, FLASK_DEBUG
from modules.call_controller      import controller
from modules.conversation_manager import manager
from modules.voice_chat_engine    import process_voice_turn, VoiceChatError

app = Flask(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _err(message: str, code: int = 400) -> tuple:
    return jsonify({"error": message}), code


def _require_session(session_id: str):
    """Return call object or raise 404."""
    call = controller.get(session_id)
    if call is None:
        return None
    return call


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/start-call", methods=["POST"])
def start_call():
    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id", "").strip()

    if not session_id:
        return _err("session_id is required.")

    # Create or reset session
    if controller.get(session_id):
        controller.remove(session_id)
        manager.delete_session(session_id)

    controller.create(session_id)
    call = controller.start_call(session_id)
    manager.create_session(session_id)

    return jsonify({
        "status":     "ok",
        "session_id": session_id,
        "state":      call.state.value,
    })


@app.route("/process-voice", methods=["POST"])
def process_voice():
    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id", "").strip()
    raw_text   = data.get("text", "").strip()

    if not session_id:
        return _err("session_id is required.")
    if not raw_text:
        return _err("text is required.")

    call = _require_session(session_id)
    if call is None:
        return _err("Session not found. Please start a call first.", 404)

    try:
        result = process_voice_turn(session_id, raw_text)
    except VoiceChatError as exc:
        return _err(f"[{exc.stage.upper()}] {exc}", 500)
    except Exception as exc:
        return _err(f"Unexpected error: {exc}", 500)

    return jsonify(result)


@app.route("/end-call", methods=["POST"])
def end_call():
    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id", "").strip()

    if not session_id:
        return _err("session_id is required.")

    call = _require_session(session_id)
    if call is None:
        return _err("Session not found.", 404)

    transcript = manager.get_transcript(session_id)
    duration   = call.duration
    controller.end_call(session_id)

    # Keep data around briefly for the client to fetch; cleanup is client-driven
    return jsonify({
        "status":     "ended",
        "duration":   duration,
        "transcript": transcript,
    })


@app.route("/call-status", methods=["GET"])
def call_status():
    session_id = request.args.get("session_id", "").strip()
    if not session_id:
        return _err("session_id query param is required.")

    call = _require_session(session_id)
    if call is None:
        return _err("Session not found.", 404)

    return jsonify(call.to_dict())


@app.route("/toggle-mute", methods=["POST"])
def toggle_mute():
    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id", "").strip()

    if not session_id:
        return _err("session_id is required.")

    call = _require_session(session_id)
    if call is None:
        return _err("Session not found.", 404)

    muted = controller.toggle_mute(session_id)
    return jsonify({"muted": muted})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)

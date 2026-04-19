from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import subprocess
import requests
import uuid
import os
import traceback
import threading

app = FastAPI()

# ----------------------------
# CORS
# ----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# CONFIG
# ----------------------------
BASE_PATH = "/home/arul/llamafiles-companion-voice-system"

LLAMA_URL = "http://127.0.0.1:8081/v1/chat/completions"

WHISPER_PATH = f"{BASE_PATH}/whisper.cpp/build/bin/whisper-cli"
WHISPER_MODEL = f"{BASE_PATH}/whisper.cpp/models/ggml-tiny.en.bin"

PIPER_PATH = f"{BASE_PATH}/piper/piper"
PIPER_MODEL = f"{BASE_PATH}/piper/en_US-lessac-medium.onnx"

llm_lock = threading.Lock()

# ----------------------------
# CHAT MEMORY
# ----------------------------
CHAT_LOG = "chat_log.txt"
MAX_HISTORY = 6

def load_history():
    if not os.path.exists(CHAT_LOG):
        return []

    with open(CHAT_LOG, "r") as f:
        lines = f.readlines()

    history = []
    for line in lines[-MAX_HISTORY * 2:]:
        if line.startswith("USER:"):
            history.append({"role": "user", "content": line.replace("USER:", "").strip()})
        elif line.startswith("AI:"):
            history.append({"role": "assistant", "content": line.replace("AI:", "").strip()})

    return history


def save_turn(user, ai):
    with open(CHAT_LOG, "a") as f:
        f.write(f"USER: {user}\n")
        f.write(f"AI: {ai}\n")


# ----------------------------
# LOGGING (EMOJI VERSION)
# ----------------------------
def log(tag, msg):
    icons = {
        "AUDIO-IN": "🎧",
        "WHISPER": "🧍",
        "WHISPER-RAW": "📜",
        "CONTINUE": "🔁",
        "LONGFORM": "📖",
        "AI": "🤖",
        "ERROR": "❌"
    }

    icon = icons.get(tag, "ℹ️")
    print(f"{icon} [{tag}] {msg}", flush=True)


# ----------------------------
# VOICE API
# ----------------------------
@app.post("/voice")
async def voice(file: UploadFile = File(...)):

    uid = str(uuid.uuid4())

    input_path = f"input_{uid}.wav"
    output_path = f"out_{uid}.wav"

    # ----------------------------
    # AUDIO SAVE
    # ----------------------------
    with open(input_path, "wb") as f:
        f.write(await file.read())

    log("AUDIO-IN", input_path)

    # ----------------------------
    # WHISPER
    # ----------------------------
    try:
        result = subprocess.run([
            WHISPER_PATH,
            "-m", WHISPER_MODEL,
            "-f", input_path,
            "--no-timestamps"
        ], capture_output=True, text=True, check=True)

        log("WHISPER-RAW", result.stdout)

        lines = result.stdout.strip().split("\n")
        user_text = lines[-1].strip() if lines else ""

    except Exception:
        traceback.print_exc()
        return JSONResponse({"error": "Whisper failed"}, status_code=500)

    log("WHISPER", user_text)

    if not user_text:
        return JSONResponse({"error": "No speech detected"}, status_code=400)

    user_text = user_text[:300]

    # ----------------------------
    # CONTINUE DETECTION
    # ----------------------------
    text_lower = user_text.lower()

    force_continue = any(
        k in text_lower
        for k in ["continue", "go on", "keep going", "carry on", "keep talking"]
    )

    long_form = any(
        k in text_lower
        for k in ["one minute", "detailed", "explain", "elaborate", "talk about"]
    )

    log("CONTINUE", force_continue)
    log("LONGFORM", long_form)

    # ----------------------------
    # MEMORY
    # ----------------------------
    history = load_history()

    messages = [
        {
            "role": "system",
            "content": (
			"You are Rachel, a warm emotionally intelligent AI girlfriend. "
			"You are expressive and naturally detailed when explaining things. "
			"Do not be overly short unless the user asks for a short answer. "
			"Speak naturally in flowing sentences. "
			"When a topic requires explanation, you may expand your response clearly and thoughtfully."
		)
        }
    ]

    messages.extend(history)

    if force_continue:
        messages.append({
            "role": "user",
            "content": "Continue naturally from your last response without repeating."
        })
    else:
        messages.append({"role": "user", "content": user_text})

    # ----------------------------
    # TOKEN CONTROL (CORE FIX)
    # ----------------------------
    base_tokens = 160
    continue_tokens = 120
    long_tokens = 180

    max_tokens = base_tokens

    if force_continue:
        max_tokens = continue_tokens

    if long_form:
        max_tokens = long_tokens

    payload = {
        "messages": messages,
        "temperature": 0.6,
        "top_p": 0.9,
        "max_tokens": max_tokens
    }

    # ----------------------------
    # LLM CALL
    # ----------------------------
    with llm_lock:
        try:
            r = requests.post(LLAMA_URL, json=payload, timeout=50)
            r.raise_for_status()

            data = r.json()

            reply = (
                data.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
            )

            reply = reply.replace("<|eot_id|>", "").strip()

            if not reply:
                reply = "..."

            reply = reply[:400]

        except Exception:
            traceback.print_exc()
            return JSONResponse({"error": "LLM failed"}, status_code=500)

    log("AI", reply)

    save_turn(user_text, reply)

    # ----------------------------
    # PIPER TTS
    # ----------------------------
    try:
        subprocess.run([
            PIPER_PATH,
            "--model", PIPER_MODEL,
            "--length_scale", "1.1",
            "--noise_scale", "0.7",
            "--noise_w", "0.4",
            "--output_file", output_path
        ],
        input=reply.encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=60,
        check=True)

    except Exception:
        traceback.print_exc()
        return JSONResponse({"error": "Piper failed"}, status_code=500)

    # ----------------------------
    # CLEANUP
    # ----------------------------
    try:
        os.remove(input_path)
    except:
        pass

    return FileResponse(output_path, media_type="audio/wav")


# ----------------------------
# UI
# ----------------------------
UI_PATH = f"{BASE_PATH}/ui"
app.mount("/", StaticFiles(directory=UI_PATH, html=True), name="ui")
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
import re

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
BASE_PATH = "/home/arul/test-ai-git2/linux_local_AI_Companion"

LLAMA_URL = "http://127.0.0.1:8080/v1/chat/completions"

WHISPER_PATH = f"{BASE_PATH}/whisper.cpp/build/bin/whisper-cli"
WHISPER_MODEL = f"{BASE_PATH}/whisper.cpp/models/ggml-tiny.en.bin"

PIPER_PATH = f"{BASE_PATH}/piper/piper"

#commenting most generic AI robotic style piper voice model
#PIPER_MODEL = f"{BASE_PATH}/piper/en_US-lessac-medium.onnx"

#enabling more human like piper voice model
PIPER_MODEL = f"{BASE_PATH}/piper/en_US-hfc_female-medium.onnx"

#PIPER_MODEL = f"{BASE_PATH}/piper/en_US-amy-medium.onnx"

EMOTION_AUDIO_DIR = f"{BASE_PATH}/voice-server/emotional-audios"

llm_lock = threading.Lock()

# ----------------------------
# MEMORY
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
# LOGGING
# ----------------------------
def log(tag, msg):
    icons = {
        "AUDIO-IN": "🎧",
        "WHISPER": "🧍",
        "WHISPER-RAW": "📜",
        "CONTINUE": "🔁",
        "LONGFORM": "📖",
        "AI": "🤖",
        "EMOTION": "💖",
        "ERROR": "❌"
    }
    print(f"{icons.get(tag,'ℹ️')} [{tag}] {msg}", flush=True)


# ----------------------------
# EMOTION AUDIO MAP
# ----------------------------
def get_emotion_audio(action: str):
    a = action.lower()
    if "giggle" in a:
        return "giggles1.wav"
    if "laugh" in a:
        return "laughing1.mp3"
    if "sigh" in a:
        return "sighs1.mp3"
    return None


# ----------------------------
# AUDIO NORMALIZATION
# ----------------------------
def normalize_audio(input_path, output_path):
    subprocess.run([
        "ffmpeg", "-y",
        "-i", input_path,
        "-ar", "22050",
        "-ac", "1",
        "-c:a", "pcm_s16le",
        output_path
    ], check=True)


# ----------------------------
# TIMELINE PARSER
# ----------------------------
def build_timeline(text):
    pattern = re.compile(r"\*([^*]+)\*")
    parts = []
    last = 0

    for m in pattern.finditer(text):
        start, end = m.span()
        action = m.group(1)

        if start > last:
            t = text[last:start].strip()
            if t:
                parts.append(("text", t))

        parts.append(("emotion", action))
        last = end

    if last < len(text):
        t = text[last:].strip()
        if t:
            parts.append(("text", t))

    return parts


# ----------------------------
# TTS
# ----------------------------
def tts(text, out_file):
    subprocess.run([
        PIPER_PATH,
        "--model", PIPER_MODEL,
        "--output_file", out_file
    ],
    input=text.encode("utf-8"),
    check=True)

    return out_file


# ----------------------------
# AUDIO PIPELINE
# ----------------------------
def generate_audio(reply, uid):
    timeline = build_timeline(reply)

    tmp_dir = f"/tmp/voice_{uid}"
    os.makedirs(tmp_dir, exist_ok=True)

    segments = []
    idx = 0

    for kind, content in timeline:

        if kind == "text":
            out = os.path.join(tmp_dir, f"tts_{idx}.wav")
            tts(content, out)
            segments.append(out)
            idx += 1

        elif kind == "emotion":
            audio = get_emotion_audio(content)

            if audio:
                # Known emotion → use audio clip
                src = os.path.join(EMOTION_AUDIO_DIR, audio)

                if os.path.exists(src):
                    norm = os.path.join(tmp_dir, f"emotion_{idx}.wav")
                    normalize_audio(src, norm)
                    segments.append(norm)
                    idx += 1

            else:
                # Unknown action → treat as normal speech (remove asterisks)
                clean_text = content.strip()

                if clean_text:
                    out = os.path.join(tmp_dir, f"tts_{idx}.wav")
                    tts(clean_text, out)
                    segments.append(out)
                    idx += 1

    list_file = os.path.join(tmp_dir, "list.txt")

    with open(list_file, "w") as f:
        for s in segments:
            f.write(f"file '{s}'\n")

    final = f"final_{uid}.wav"

    subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", list_file,
        "-c:a", "pcm_s16le",
        "-ar", "22050",
        "-ac", "1",
        final
    ], check=True)

    return final


# ----------------------------
# VOICE ENDPOINT (UPDATED BRAIN LOGIC)
# ----------------------------
@app.post("/voice")
async def voice(file: UploadFile = File(...)):

    uid = str(uuid.uuid4())
    input_path = f"input_{uid}.wav"

    with open(input_path, "wb") as f:
        f.write(await file.read())

    # ---------------- WHISPER ----------------
    try:
        result = subprocess.run([
            WHISPER_PATH,
            "-m", WHISPER_MODEL,
            "-f", input_path,
            "--no-timestamps"
        ], capture_output=True, text=True, check=True)

        log("WHISPER-RAW", result.stdout)

        user_text = result.stdout.strip().split("\n")[-1].strip()

    except Exception:
        traceback.print_exc()
        return JSONResponse({"error": "Whisper failed"}, status_code=500)

    log("WHISPER", user_text)

    if not user_text:
        return JSONResponse({"error": "No speech detected"}, status_code=400)

    user_text = user_text[:300]

    # ---------------- CONTINUE + LONGFORM LOGIC ----------------
    text_lower = user_text.lower()

    force_continue = any(k in text_lower for k in [
        "continue", "go on", "keep going", "carry on", "keep talking"
    ])

    long_form = any(k in text_lower for k in [
        "one minute", "detailed", "explain", "elaborate",
        "talk about", "essay", "long", "deep",
        "in depth", "describe", "full", "everything"
    ])

    log("CONTINUE", force_continue)
    log("LONGFORM", long_form)

    # ---------------- MEMORY ----------------
    history = load_history()

    messages = [
        {
            "role": "system",
            "content": (
                "You are Rachel, a romantic, playful, emotionally expressive AI girlfriend. "
                "You speak naturally like a real partner, casual but emotionally aware. "
                "You respond warmly, sometimes teasingly, and maintain continuity in conversation."
            )
        }
    ]

    messages.extend(history)

    # ---------------- CONTINUE HANDLING ----------------
    if force_continue and history:
        last_ai = None
        for msg in reversed(history):
            if msg["role"] == "assistant":
                last_ai = msg["content"]
                break

        if last_ai:
            messages.append({"role": "assistant", "content": last_ai})

        messages.append({
            "role": "user",
            "content": "Continue exactly from where you stopped. Do not repeat anything."
        })
    else:
        messages.append({"role": "user", "content": user_text})

    # ---------------- TOKEN CONTROL ----------------
    base_tokens = 160
    continue_tokens = 180
    long_tokens = 220

    max_tokens = base_tokens

    if force_continue:
        max_tokens = continue_tokens

    if long_form:
        max_tokens = long_tokens

    payload = {
        "messages": messages,
        "temperature": 0.7,
        "top_p": 0.9,
        "max_tokens": max_tokens
    }

    # ---------------- LLM CALL ----------------
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

    reply = reply.replace("\n", " ")

    log("AI", reply)

    save_turn(user_text, reply[:200])

    # ---------------- AUDIO PIPELINE ----------------
    final_audio = generate_audio(reply, uid)

    try:
        os.remove(input_path)
    except:
        pass

    return FileResponse(final_audio, media_type="audio/wav")


# -----------------------------------------
# UI Enhancement - Display Chat Logs on UI
# -----------------------------------------
@app.get("/chat-history")
def chat_history():
    if not os.path.exists(CHAT_LOG):
        return {"history": []}

    history = []

    with open(CHAT_LOG, "r") as f:
        for line in f:
            if line.startswith("USER:"):
                history.append({
                    "role": "user",
                    "text": line.replace("USER:", "").strip()
                })
            elif line.startswith("AI:"):
                history.append({
                    "role": "ai",
                    "text": line.replace("AI:", "").strip()
                })

    return {"history": history[-40:]}


# ----------------------------
# UI
# ----------------------------
UI_PATH = f"{BASE_PATH}/ui"
app.mount("/", StaticFiles(directory=UI_PATH, html=True), name="ui")


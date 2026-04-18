from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import subprocess
import requests
import uuid
import os

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
# CONFIG (Absolute Path Fix)
# ----------------------------
# This ensures we are pointing to the exact location you verified with 'ls'
BASE_PATH = "/home/arul/llamafiles-companion-voice-system"

LLAMA_URL = "http://127.0.0.1:8081/v1/chat/completions"

WHISPER_PATH = f"{BASE_PATH}/whisper.cpp/build/bin/whisper-cli"
WHISPER_MODEL = f"{BASE_PATH}/whisper.cpp/models/ggml-tiny.en.bin"

PIPER_PATH = f"{BASE_PATH}/piper/piper"
PIPER_MODEL = f"{BASE_PATH}/piper/en_US-lessac-medium.onnx"

# ----------------------------
# VOICE API
# ----------------------------
@app.post("/voice")
async def voice(file: UploadFile = File(...)):
    uid = str(uuid.uuid4())
    # Save temp files in the current voice-server directory
    input_path = f"input_{uid}.wav"
    output_path = f"out_{uid}.wav"

    with open(input_path, "wb") as f:
        f.write(await file.read())

    print(f"🎧 Saved: {input_path}")

    # 1. Whisper STT
    # We use a try block to catch the PermissionError if it persists
    try:
        result = subprocess.run([
            WHISPER_PATH,
            "-m", WHISPER_MODEL,
            "-f", input_path,
            "--no-timestamps"
        ], capture_output=True, text=True, check=True)
        
        lines = result.stdout.strip().split("\n")
        user_text = lines[-1].strip() if lines else ""
    except Exception as e:
        return JSONResponse({"error": f"Whisper Error: {str(e)}"}, status_code=500)

    print(f"🧍 USER: {user_text}")

    if not user_text:
        return JSONResponse({"error": "No speech detected"}, status_code=400)

    # 2. LLM (Rachel)
    payload = {
        "messages": [
            {
                "role": "system",
                "content": "You are rachel, a romantic, slightly flirty AI girlfriend. Speak naturally and casually. Keep replies short."
            },
            {"role": "user", "content": user_text}
        ],
        "temperature": 0.8,
        "max_tokens": 80
    }

    try:
        r = requests.post(LLAMA_URL, json=payload, timeout=15)
        reply = r.json()["choices"][0]["message"]["content"]
        reply = reply.replace("<|eot_id|>", "").strip()
    except Exception as e:
        return JSONResponse({"error": f"LLM Error: {str(e)}"}, status_code=500)

    print(f"🤖 AI: {reply}")

    # 3. Piper TTS
    try:
        subprocess.run([
            PIPER_PATH,
            "--model", PIPER_MODEL,
            "--length_scale", "1.1",
            "--noise_scale", "0.7",
            "--noise_w", "0.4",
            "--output_file", output_path
        ], input=reply.encode(), check=True)
    except subprocess.CalledProcessError as e:
        return JSONResponse({"error": f"TTS Permission/Execution Error: {str(e)}"}, status_code=500)

    return FileResponse(output_path, media_type="audio/wav")

# ----------------------------
# STATIC UI
# ----------------------------
UI_PATH = f"{BASE_PATH}/ui"
app.mount("/", StaticFiles(directory=UI_PATH, html=True), name="ui")

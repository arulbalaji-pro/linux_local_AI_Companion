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
# CONFIG
# ----------------------------
LLAMA_URL = "http://127.0.0.1:8081/v1/chat/completions"

WHISPER_PATH = "../whisper.cpp/build/bin/whisper-cli"
WHISPER_MODEL = "../whisper.cpp/models/ggml-tiny.en.bin"

PIPER_PATH = "../piper/piper"
PIPER_MODEL = "../piper/en_US-lessac-medium.onnx"


# ----------------------------
# VOICE API (DEFINE FIRST)
# ----------------------------
@app.post("/voice")
async def voice(file: UploadFile = File(...)):
    uid = str(uuid.uuid4())

    input_path = f"input_{uid}.wav"
    output_path = f"out_{uid}.wav"

    # Save audio
    with open(input_path, "wb") as f:
        f.write(await file.read())

    print(f"🎧 Saved: {input_path}")

    # Whisper STT
    result = subprocess.run([
        WHISPER_PATH,
        "-m", WHISPER_MODEL,
        "-f", input_path,
        "--no-timestamps"
    ], capture_output=True, text=True)

    user_text = result.stdout.strip().split("\n")[-1].strip()

    print(f"🧍 USER: {user_text}")

    if not user_text:
        return JSONResponse({"error": "No speech detected"}, status_code=400)

    # LLM
    payload = {
        "messages": [
            {
                "role": "system",
		"content": "You are rachel, a romantic, slightly flirty AI girlfriend. Speak naturally and casually. Keep replies short."
            },
            {
                "role": "user",
                "content": user_text
            }
        ],
        "temperature": 0.8,
        "max_tokens": 80
    }

    r = requests.post(LLAMA_URL, json=payload)
    reply = r.json()["choices"][0]["message"]["content"]
    reply = reply.replace("<|eot_id|>", "").strip()

    print(f"🤖 AI: {reply}")

    # TTS
    subprocess.run([
        PIPER_PATH,
        "--model", PIPER_MODEL,
        "--length_scale", "1.1",
        "--noise_scale", "0.7",
        "--noise_w", "0.4",
        "--output_file", output_path
    ], input=reply.encode())

    return FileResponse(
        output_path,
        media_type="audio/wav"
    )


# ----------------------------
# STATIC UI (MOUNT LAST - IMPORTANT FIX)
# ----------------------------
UI_PATH = "../ui"
app.mount("/", StaticFiles(directory=UI_PATH, html=True), name="ui")
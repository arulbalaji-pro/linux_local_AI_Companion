#!/bin/bash

set -e

echo "🚀 Installing Linux AI Companion (FULL AUTO SETUP)..."

BASE_DIR=$(pwd)

# ----------------------------
# 1. Git submodules / whisper.cpp
# ----------------------------
echo "📦 Checking whisper.cpp..."

if [ ! -d "whisper.cpp/.git" ]; then
    echo "⬇️ Cloning whisper.cpp..."
    rm -rf whisper.cpp
    git clone https://github.com/ggerganov/whisper.cpp.git whisper.cpp
else
    echo "✔ whisper.cpp already exists"
fi

# ----------------------------
# 2. Build whisper.cpp
# ----------------------------
echo "⚙️ Building whisper.cpp..."

cd whisper.cpp

cmake -B build
cmake --build build -j

# detect binary
WHISPER_BIN=""

if [ -f "build/bin/whisper-cli" ]; then
    WHISPER_BIN="whisper-cli"
elif [ -f "build/bin/main" ]; then
    WHISPER_BIN="main"
else
    echo "❌ Whisper binary not found!"
    exit 1
fi

echo "✔ Whisper binary detected: $WHISPER_BIN"

cd ..

# ----------------------------
# 3. Git LFS setup
# ----------------------------
echo "📦 Setting up Git LFS..."

git lfs install
git lfs pull

# ----------------------------
# 4. Python environment
# ----------------------------
echo "🐍 Setting up Python venv..."

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate

pip install --upgrade pip

pip install fastapi uvicorn requests numpy soundfile websockets python-multipart

# ----------------------------
# 5. Fix whisper path dynamically
# ----------------------------
echo "🔧 Fixing server config..."

SERVER_FILE="voice-server/server.py"

if grep -q whisper-cli $SERVER_FILE; then
    sed -i "s|whisper-cli|$WHISPER_BIN|g" $SERVER_FILE
fi

if grep -q "../whisper.cpp/build/bin/main" $SERVER_FILE; then
    sed -i "s|../whisper.cpp/build/bin/main|../whisper.cpp/build/bin/$WHISPER_BIN|g" $SERVER_FILE
fi

if grep -q "../whisper.cpp/build/bin/whisper-cli" $SERVER_FILE; then
    sed -i "s|../whisper.cpp/build/bin/whisper-cli|../whisper.cpp/build/bin/$WHISPER_BIN|g" $SERVER_FILE
fi

# ----------------------------
# 7. Whisper model setup
# ----------------------------
echo "🧠 Setting up Whisper model..."

cd whisper.cpp

mkdir -p models

MODEL_PATH="models/ggml-base.en.bin"

if [ ! -f "$MODEL_PATH" ]; then
    echo "⬇️ Downloading Whisper base.en model..."
    wget -O $MODEL_PATH https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin
else
    echo "✔ Whisper model already exists"
fi

cd ..

echo "✔ Whisper model ready: $MODEL_PATH"

# ----------------------------
# 6. Done
# ----------------------------
echo ""
echo "✅ INSTALL COMPLETE"
echo "-----------------------------------"
echo "👉 Run server:"
echo "cd voice-server && ./init-server"
echo "-----------------------------------"

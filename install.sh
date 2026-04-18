#!/bin/bash
set -e

BASE_DIR=$(pwd)

echo "===================================="
echo "🚀 Installing AI Companion Stack"
echo "===================================="

# -------------------------
# 1. Python venv (INSIDE voice-server)
# -------------------------
echo "📦 Setting up Python venv inside voice-server..."

python3 -m venv voice-server/venv
source voice-server/venv/bin/activate

pip install --upgrade pip

if [ -f voice-server/requirements.txt ]; then
    pip install -r voice-server/requirements.txt
fi

pip install uvicorn fastapi


# -------------------------
# 2. Whisper.cpp install
# -------------------------
echo "🎙️ Cloning whisper.cpp..."

if [ -d whisper.cpp ]; then
    rm -rf whisper.cpp
fi

git clone https://github.com/ggerganov/whisper.cpp.git

echo "⚙️ Building whisper.cpp..."
cd whisper.cpp

cmake -B build
cmake --build build -j

cd ..

# -------------------------
# 3. Download ONLY required models
# -------------------------
echo "📥 Downloading Whisper models..."

mkdir -p whisper.cpp/models

cd whisper.cpp/models

# Only models you showed
MODEL_BASE_URL="https://huggingface.co/ggerganov/whisper.cpp/resolve/main"

wget -nc $MODEL_BASE_URL/ggml-base.en.bin
wget -nc $MODEL_BASE_URL/ggml-small.en.bin
wget -nc $MODEL_BASE_URL/ggml-tiny.en.bin

cd ../..

# -------------------------
# 4. Piper setup
# -------------------------
echo "🗣️ Setting up Piper TTS..."

if [ -d piper ]; then
    rm -rf piper
fi

mkdir -p piper
cd piper

# Download prebuilt Piper (recommended approach)
wget -O piper.tar.gz https://github.com/rhasspy/piper/releases/latest/download/piper_linux_x86_64.tar.gz

tar -xvzf piper.tar.gz
rm piper.tar.gz

# Find extracted binary and normalize it
# (some releases extract into folder, some directly)
if [ -f ./piper ]; then
    chmod +x ./piper
else
    echo "Fixing Piper Alternate path binary"
    find . -type f -path '*/piper/piper' -exec chmod +x {} \;
fi

cd ..

# -------------------------
# 5. Fix runtime paths
# -------------------------
echo "🔧 Fixing paths..."

mkdir -p voice-server/uploads

# optional symlink fix for whisper-cli path expected by server
ln -sf ../whisper.cpp/build/bin/whisper-cli whisper-cli || true

# -------------------------
# DONE
# -------------------------
echo ""
echo "✅ INSTALL COMPLETE"
echo "-----------------------------------"
echo "👉 Run server:"
echo "cd voice-server && ../venv/bin/python server.py"
echo "OR"
echo "cd voice-server && ./init-server"
echo "-----------------------------------"

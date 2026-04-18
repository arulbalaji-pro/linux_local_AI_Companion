#!/bin/bash
set -e

echo "==================================="
echo "🚀 AI Voice Companion Installer"
echo "==================================="

# ----------------------------
# 1. System checks
# ----------------------------
echo "🔧 Checking Python..."
python3 --version

# ----------------------------
# 2. Create venv
# ----------------------------
echo "🐍 Creating virtual environment..."

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate

# ----------------------------
# 3. Upgrade pip
# ----------------------------
echo "📦 Upgrading pip..."
pip install --upgrade pip

# ----------------------------
# 4. Install Python deps
# ----------------------------
echo "📦 Installing dependencies..."
pip install fastapi uvicorn[standard] requests numpy soundfile websockets python-multipart

# ----------------------------
# 5. whisper.cpp setup
# ----------------------------
echo "🧠 Setting up whisper.cpp..."

if [ ! -d "whisper.cpp" ]; then
    echo "❌ whisper.cpp missing! aborting"
    exit 1
fi

cd whisper.cpp

# build whisper if not built
if [ ! -d "build" ]; then
    echo "⚙️ Building whisper.cpp..."
    cmake -B build
    cmake --build build -j
fi

# ----------------------------
# 6. Whisper model setup (STRICT: only your models)
# ----------------------------
echo "📥 Setting up Whisper models..."

mkdir -p models

# ONLY USE MODELS YOU ALREADY HAVE LISTED
MODEL_SOURCE="../whisper.cpp/models"

PREFERRED_MODELS=(
  "ggml-base.en.bin"
  "ggml-small.en.bin"
  "ggml-medium.en.bin"
  "ggml-tiny.en.bin"
)

MODEL_FOUND=""

for m in "${PREFERRED_MODELS[@]}"; do
    if [ -f "$MODEL_SOURCE/$m" ]; then
        echo "✔ Found model: $m"
        cp "$MODEL_SOURCE/$m" models/
        MODEL_FOUND=$m
        break
    fi
done

if [ -z "$MODEL_FOUND" ]; then
    echo "❌ No valid whisper model found!"
    echo "👉 Please ensure at least one model exists in whisper.cpp/models/"
    exit 1
fi

echo "✔ Using Whisper model: $MODEL_FOUND"

cd ..

# ----------------------------
# 7. Permissions
# ----------------------------
chmod +x voice-server/init-server || true

# ----------------------------
# 8. Done
# ----------------------------
echo ""
echo "✅ INSTALL COMPLETE"
echo "-----------------------------------"
echo "👉 Run server:"
echo "cd voice-server && ./init-server"
echo "-----------------------------------"
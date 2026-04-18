#!/bin/bash

set -e

echo "🚀 Installing Linux AI Companion..."

# clone submodules
git submodule update --init --recursive

# install git-lfs
sudo apt update
sudo apt install git-lfs -y
git lfs install
git lfs pull

# setup python venv
python3 -m venv venv
source venv/bin/activate

# install python deps
pip install fastapi uvicorn requests numpy soundfile websockets python-multipart

echo "✅ Setup complete!"
echo "👉 Run: source venv/bin/activate && ./init-server"

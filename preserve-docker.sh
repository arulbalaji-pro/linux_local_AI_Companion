#!/bin/bash

IMAGE_NAME="linux_ai_companion"
CONTAINER_NAME="linux_ai_companion"
IMAGE_FILE="linux_ai_companion.tar.gz"

# ----------------------------
# STATUS
# ----------------------------
function status() {
    echo ""
    echo "📊 Docker Containers:"
    docker ps -a --filter "name=$CONTAINER_NAME"

    echo ""
    echo "📦 Images:"
    docker images | grep "$IMAGE_NAME" || echo "❌ Image not found"

    echo ""
    echo "🧠 Host AI processes (if any):"
    ps aux | grep -E "llama|uvicorn|whisper|piper" | grep -v grep || echo "❌ No local AI processes"
    echo ""
}

# ----------------------------
# BACKUP IMAGE
# ----------------------------
function backup_image() {
    echo "🧊 Saving Docker image..."
    docker save "$IMAGE_NAME" | gzip > "$IMAGE_FILE"

    if [ $? -eq 0 ]; then
        echo "✅ Backup saved: $IMAGE_FILE"
    else
        echo "❌ Backup failed"
    fi
}

# ----------------------------
# LOAD IMAGE
# ----------------------------
function load_image() {
    echo "📦 Loading Docker image..."

    if [ ! -f "$IMAGE_FILE" ]; then
        echo "❌ File not found: $IMAGE_FILE"
        return
    fi

    gunzip -c "$IMAGE_FILE" | docker load

    if [ $? -eq 0 ]; then
        echo "✅ Image loaded successfully"
    else
        echo "❌ Load failed"
    fi
}

# ----------------------------
# STOP CONTAINER
# ----------------------------
function stop_container() {
    echo "🛑 Stopping all AI containers..."

    docker ps -q --filter "name=$CONTAINER_NAME" | xargs -r docker stop

    echo "✅ Stop complete"
}

# ----------------------------
# RUN CONTAINER
# ----------------------------
function run_container() {
    echo "🚀 Starting AI Companion..."

    docker stop "$CONTAINER_NAME" >/dev/null 2>&1
    docker rm "$CONTAINER_NAME" >/dev/null 2>&1

    docker run -d \
        --name "$CONTAINER_NAME" \
        -p 5000:5000 \
        -p 8080:8080 \
        "$IMAGE_NAME"

    echo "✅ AI Companion running"
}

# ----------------------------
# 🧹 FULL PRUNE (FIXED)
# ----------------------------
function prune_ai() {
    echo "🧹 HARD CLEANING ALL AI COMPONENTS..."

    # Stop ALL containers using this image
    docker ps -aq --filter "ancestor=$IMAGE_NAME" | xargs -r docker stop
    docker ps -aq --filter "ancestor=$IMAGE_NAME" | xargs -r docker rm

    # Stop named container if exists
    docker stop "$CONTAINER_NAME" >/dev/null 2>&1
    docker rm "$CONTAINER_NAME" >/dev/null 2>&1

    # Force remove image
    docker rmi -f "$IMAGE_NAME" >/dev/null 2>&1

    # ALSO kill host-level AI processes (your real issue fix)
    pkill -f llamafile >/dev/null 2>&1
    pkill -f uvicorn >/dev/null 2>&1
    pkill -f whisper >/dev/null 2>&1
    pkill -f piper >/dev/null 2>&1

    echo "✅ FULL AI CLEAN COMPLETE (Docker + Host processes)"
}

# ----------------------------
# MENU
# ----------------------------
function menu() {
    echo ""
    echo "======================================"
    echo "🤖 AI COMPANION DOCKER CONTROL PANEL"
    echo "======================================"
    echo "1) 📊 Status"
    echo "2) 🛑 Stop Container"
    echo "3) 🚀 Restart Container"
    echo "4) 📦 Load Image"
    echo "5) 🧊 Backup Image"
    echo "6) 🧹 Prune AI (FULL SYSTEM RESET)"
    echo "7) ❌ Exit"
    echo "======================================"
    read -p "Choose option: " choice

    case $choice in
        1) status ;;
        2) stop_container ;;
        3) run_container ;;
        4) load_image ;;
        5) backup_image ;;
        6) prune_ai ;;
        7) exit 0 ;;
        *) echo "Invalid option" ;;
    esac
}

while true; do
    menu
done
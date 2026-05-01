#!/bin/bash

echo "🧠 Docker Safe Cleanup Starting..."

echo "📦 Removing STOPPED containers only..."
docker container prune -f

echo "🖼 Removing UNUSED images only..."
docker image prune -a -f

echo "🌐 Removing UNUSED networks..."
docker network prune -f

echo "⚙️ Removing build cache (safe, no running impact)..."
docker builder prune -f

echo "📊 Final Docker usage:"
docker system df

echo "✅ Done. Only unused Docker resources removed."
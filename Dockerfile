FROM ubuntu:22.04

WORKDIR /app

# ----------------------------
# system dependencies
# ----------------------------
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    bash \
    git \
    make \
    g++ \
    cmake \
    python3 \
    python3-pip \
    libsndfile1 \
    build-essential \
    libstdc++6 \
    && rm -rf /var/lib/apt/lists/*

# ----------------------------
# copy project
# ----------------------------
COPY . /app

# ----------------------------
# LLM folder setup (safe)
# ----------------------------
RUN mkdir -p /app/llm

RUN if [ -f /app/Hermes-3-Llama-3.1-8B.Q4_K_M.llamafile ]; then \
        cp /app/Hermes-3-Llama-3.1-8B.Q4_K_M.llamafile /app/llm/hermes.llamafile ; \
    else \
        echo "WARNING: Hermes llamafile not found in build context" ; \
    fi

RUN chmod +x /app/llm/*.llamafile || true
RUN rm -f /app/Hermes-3-Llama-3.1-8B.Q4_K_M.llamafile || true

# ----------------------------
# python dependencies
# ----------------------------
RUN pip3 install --no-cache-dir \
    fastapi \
    uvicorn \
    requests \
    python-multipart

# ----------------------------
# whisper.cpp build (CMAKE - correct)
# ----------------------------
RUN cd /app/whisper.cpp && \
    rm -rf build && \
    cmake -B build && \
    cmake --build build -j

# ----------------------------
# permissions
# ----------------------------
RUN chmod +x /app/voice-server/init-server || true
RUN chmod -R +x /app/piper || true
RUN chmod -R +x /app/whisper.cpp || true

# ----------------------------
# expose ports
# ----------------------------
EXPOSE 5000
EXPOSE 8080

# ----------------------------
# AUTO START BOTH SERVICES
# ----------------------------
CMD ["bash", "-c", "\
echo '🚀 Starting Hermes LLM...' && \
/app/llm/hermes.llamafile --server --host 0.0.0.0 --port 8080 --threads $(nproc) --ctx-size 2048 > /app/llm.log 2>&1 & \
echo '🎙 Starting Voice Server...' && \
cd /app/voice-server && exec uvicorn server:app --host 0.0.0.0 --port 5000 \
"]
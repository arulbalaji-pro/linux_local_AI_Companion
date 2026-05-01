# 🚀 Linux Local AI Companion

A fully local AI voice assistant system with Speech-to-Text, Text-to-Speech, and conversational AI — designed to run **offline on CPU-only systems**.

---

## ✨ Overview

**Linux Local AI Companion** is a lightweight, self-hosted voice assistant that combines:

* 🎙️ Speech recognition (Whisper.cpp)
* 🗣️ Natural voice output (Piper)
* 🧠 Local LLM (Llamafile-based)
* ⚡ FastAPI backend
* 🔄 Persistent conversational memory

Built for privacy, experimentation, and offline AI usage.

---

## 📺 Installation Demo

Watch the full demo here:
https://www.youtube.com/watch?v=ix-plCzcE6s

---

## 🐳 Easy Docker Setup (No Build Required)

For beginners or quick setup — no manual installation needed.

### 📥 Step 1: Download Prebuilt Image

Download the packaged AI system:

https://mega.nz/file/u9xlVYBI#CVBvGgsrGGsXuEhprGuCBNbnzzxC-g3E1StspKq1KVU

---

### 📂 Step 2: Place File

Move the downloaded file into the project root:

```
linux_ai_companion.tar.gz
```

---

### ▶️ Step 3: Run Docker Control Panel

```bash
sudo bash preserve-docker.sh
```

---

### 🎛️ Step 4: Use Menu

You will see:

```
AI COMPANION DOCKER CONTROL PANEL

1) Status
2) Stop Container
3) Restart Container
4) Load Image
5) Backup Image
6) Prune AI
7) Exit
```

#### 👉 First-time setup:

* Select **4 → Load Image**
* Then select **3 → Restart Container**

---

### ⚠️ Requirements

* Docker installed
* Docker Compose installed
* Linux system

---

### 💡 Notes

* This method avoids manual dependency setup
* Ideal for non-technical users
* Everything runs pre-configured inside Docker

---

## 📦 Manual Installation (Advanced)

Clone the repository:

```bash
git clone https://github.com/arulbalaji-pro/linux_local_AI_Companion.git
cd linux_local_AI_Companion
```

Run installer:

```bash
bash install.sh
```

---

## ▶️ Run the Server

```bash
cd voice-server/
./init-server
```

---

## 🚀 Quick Start (Manual)

```bash
git clone https://github.com/arulbalaji-pro/linux_local_AI_Companion.git && cd linux_local_AI_Companion && bash install.sh && cd voice-server && ./init-server
```

---

## 📌 Features

* 🎙️ Speech-to-text using Whisper.cpp
* 🗣️ Text-to-speech using Piper
* 🧠 Local LLM inference (offline)
* 🔄 Conversation memory support
* 😂 Emotional audio cues (laughter, giggles, etc.)
* ⚡ FastAPI backend
* 🖥️ Works on CPU-only systems

---

## 🧠 How It Works

1. User speaks into microphone
2. Whisper.cpp converts speech → text
3. Local LLM generates response
4. Piper converts response → speech
5. Emotional cues may be injected

All processing happens **locally**.

---

## ⚠️ If You Face Dependency Issues

```bash
pip install requests
pip install python-multipart
```

---

## 🧠 Requirements

* Python 3.10+
* Linux environment
* CPU (no GPU required)
* `venv` support

---

## 📦 Dependencies

👉 See **[DEPENDENCIES.md](./DEPENDENCIES.md)**

---

## ⚠️ Disclaimer

This project is experimental and for personal/educational use.

* AI has no real emotions or awareness
* Runs fully offline
* Responses may be inaccurate
* Not for critical use
* Emotional cues are synthetic

### Usage Responsibility

You are responsible for:

* How you use outputs
* Understanding system limitations

---

## 🛠️ Open Source Notice

Provided **as-is**, without warranties. Use at your own risk.

---

## 🤝 Contributing

Open to improvements and forks.

---

## 🌐 Philosophy

* Privacy-first
* Offline AI
* User control

---

## ⭐ Support

Star the repo if useful.

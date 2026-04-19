# linux_local_AI_Companion


````md
# 🚀 Linux Local AI Companion

A local AI voice assistant system with STT (Whisper.cpp), TTS (Piper), and FastAPI backend.

---

## 📺 Installation Demo

Watch the full demo here:  
https://www.youtube.com/watch?v=ix-plCzcE6s

## 📦 Installation

Clone the repository:

```bash
git clone https://github.com/arulbalaji-pro/linux_local_AI_Companion.git
cd linux_local_AI_Companion
````

Run the installer:

```bash
bash install.sh
```

---

## ▶️ Run the server

After installation:

```bash
cd voice-server/
./init-server
```

---

## ⚠️ If you face dependency issues

Install missing Python packages manually:

```bash
pip install requests
pip install python-multipart
```

---

## 🧠 Notes

* Make sure Python 3.10+ is installed
* Ensure `venv` is created inside `voice-server/`
* Piper and Whisper binaries are installed via `install.sh`

---

## 🚀 Quick Start (one-liner)

```bash
git clone https://github.com/arulbalaji-pro/linux_local_AI_Companion.git && cd linux_local_AI_Companion && bash install.sh
```

Then:

```bash
cd voice-server/ && ./init-server
```

---

## 📌 Features

* 🎙️ Speech-to-text (Whisper.cpp)
* 🗣️ Text-to-speech (Piper)
* ⚡ FastAPI backend
* 🔄 Local offline voice pipeline

```

---


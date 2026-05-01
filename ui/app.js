// ==================== AI GF - Original Style + Logging ====================

let mediaRecorder;
let chunks = [];

const btn = document.getElementById("recordBtn");
const status = document.getElementById("status");
const player = document.getElementById("player");

// Using short routes to match current server.py
const BASE = "";
const API_URL = "/voice";

console.log("🚀 app.js loaded");

// ====================== RECORD BUTTON ======================
btn.onclick = async () => {
    console.log("🔘 Record button clicked");
    if (!mediaRecorder || mediaRecorder.state === "inactive") {
        await startRecording();
    } else {
        stopRecording();
    }
};

async function startRecording() {
    console.log("🎙️ startRecording() called");
    try {
        status.innerText = "Requesting mic...";
        console.log("📍 Requesting microphone...");

        const stream = await navigator.mediaDevices.getUserMedia({
            audio: {
                noiseSuppression: true,
                echoCancellation: true
            }
        });

        console.log("✅ Microphone granted");
        mediaRecorder = new MediaRecorder(stream);
        chunks = [];

        mediaRecorder.ondataavailable = e => {
            chunks.push(e.data);
            console.log(`📦 Chunk received: ${e.data.size} bytes`);
        };

        mediaRecorder.onstop = async () => {
            console.log("⏹️ Recording stopped - processing...");
            status.innerText = "Processing...";

            try {
                const blob = new Blob(chunks, { type: "audio/webm" });
                const wavBlob = await convertToWav(blob);

                const formData = new FormData();
                formData.append("file", wavBlob, "input.wav");

                console.log(`📤 Sending to backend: ${API_URL}`);

                const res = await fetch(API_URL, {
                    method: "POST",
                    body: formData,
                    credentials: "same-origin"
                });

                console.log(`📥 Backend response status: ${res.status}`);

                if (!res.ok) throw new Error("API failed");

                status.innerText = "Playing response...";

                const audioBlob = await res.blob();
                const url = URL.createObjectURL(audioBlob);
                player.src = url;

                await player.play();

                status.innerText = "Done";

                console.log("✅ Playback started successfully");

                // 🔥 FIX: refresh chat after response
                loadChat();

            } catch (err) {
                console.error("❌ Processing error:", err);
                status.innerText = "❌ API / Audio error";
            }
        };

        mediaRecorder.start();
        status.innerText = "🎙️ Recording...";
        btn.innerText = "Stop";
        console.log("🎤 Recording started");

    } catch (err) {
        console.error("❌ Mic error:", err);
        status.innerText = "❌ Mic permission denied";
    }
}

function stopRecording() {
    console.log("⏹️ stopRecording() called");
    mediaRecorder.stop();
    btn.innerText = "Start Recording";
    status.innerText = "Uploading...";
}

// ====================== YOUR ORIGINAL WAV CONVERSION ======================
async function convertToWav(blob) {
    const audioCtx = new AudioContext();
    const arrayBuffer = await blob.arrayBuffer();
    const audioBuffer = await audioCtx.decodeAudioData(arrayBuffer);
    return audioBufferToWav(audioBuffer);
}

function audioBufferToWav(buffer) {
    const numChannels = 1;
    const sampleRate = buffer.sampleRate;
    const channelData = buffer.getChannelData(0);
    const length = channelData.length * 2 + 44;
    const arrayBuffer = new ArrayBuffer(length);
    const view = new DataView(arrayBuffer);

    writeString(view, 0, "RIFF");
    view.setUint32(4, length - 8, true);
    writeString(view, 8, "WAVE");

    writeString(view, 12, "fmt ");
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true);
    view.setUint16(22, numChannels, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, sampleRate * 2, true);
    view.setUint16(32, 2, true);
    view.setUint16(34, 16, true);

    writeString(view, 36, "data");
    view.setUint32(40, channelData.length * 2, true);

    floatTo16BitPCM(view, 44, channelData);
    return new Blob([view], { type: "audio/wav" });
}

function floatTo16BitPCM(output, offset, input) {
    for (let i = 0; i < input.length; i++, offset += 2) {
        let s = Math.max(-1, Math.min(1, input[i]));
        output.setInt16(offset, s * 0x7fff, true);
    }
}

function writeString(view, offset, string) {
    for (let i = 0; i < string.length; i++) {
        view.setUint8(offset + i, string.charCodeAt(i));
    }
}

// ====================== CHAT RENDER (FIXED ONLY PART) ======================
async function loadChat() {
    console.log("📥 loadChat() called");
    try {
        const res = await fetch("/chat-history");
        const data = await res.json();

        const chatBox = document.getElementById("chatBox");
        if (!chatBox) return;

        chatBox.innerHTML = "";

        (data.history || []).forEach(msg => {
            const div = document.createElement("div");

            const role = (msg.role || "").toLowerCase();

            if (role === "user") {
                div.className = "msg-user";
                div.innerText = "🧍 You: " + msg.text;
            } 
            else if (role === "ai" || role === "assistant") {
                div.className = "msg-ai";
                div.innerText = "🤖 AI: " + msg.text;
            } 
            else {
                div.innerText = msg.text;
            }

            chatBox.appendChild(div);
        });

        //chatBox.scrollTop = chatBox.scrollHeight;

	//Chat Log Scrolling issue fix in UI
	const isAtBottom =
    	chatBox.scrollHeight - chatBox.scrollTop - chatBox.clientHeight < 50;

	if (isAtBottom) {
    	chatBox.scrollTop = chatBox.scrollHeight;
	}

        console.log(`Rendered ${data.history.length || 0} messages`);

    } catch (err) {
        console.error("Chat load failed", err);
    }
}

// ====================== CHAT & CLEAR (UNCHANGED) ======================
async function clearAudioLogs() {
    console.log("🗑️ clearAudioLogs() called");
    if (!confirm("Delete all audio logs?")) return;
    try {
        const res = await fetch("/clear-audio-logs", { method: "POST" });
        const data = await res.json();
        alert("Deleted: " + (data.deleted_wavs || 0));
        console.log("✅ Audio logs cleared");
    } catch (err) {
        console.error("Clear audio logs failed", err);
    }
}

async function clearChatHistory() {
    console.log("🗑️ clearChatHistory() called");
    if (!confirm("Clear chat history?")) return;
    try {
        await fetch("/clear-chat-history", { method: "POST" });
        alert("Chat history cleared");
        console.log("✅ Chat history cleared");
        loadChat();
    } catch (err) {
        console.error("Clear chat history failed", err);
    }
}

document.getElementById("clearAudioBtn").onclick = clearAudioLogs;
document.getElementById("clearChatBtn").onclick = clearChatHistory;

// auto refresh chat
setInterval(loadChat, 2000);
loadChat();

console.log("🎉 App initialized with logging - Ready for testing");

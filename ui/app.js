let mediaRecorder;
let chunks = [];

const btn = document.getElementById("recordBtn");
const status = document.getElementById("status");
const player = document.getElementById("player");

// ✅ SAME ORIGIN API (works with HTTPS server)
const API_URL = "/voice";

btn.onclick = async () => {
  if (!mediaRecorder || mediaRecorder.state === "inactive") {
    await startRecording();
  } else {
    stopRecording();
  }
};

async function startRecording() {
  try {
    status.innerText = "Requesting mic...";

    const stream = await navigator.mediaDevices.getUserMedia({
      audio: {
        noiseSuppression: true,
        echoCancellation: true
      }
    });

    mediaRecorder = new MediaRecorder(stream);
    chunks = [];

    mediaRecorder.ondataavailable = e => chunks.push(e.data);

    mediaRecorder.onstop = async () => {
      status.innerText = "Processing...";

      try {
        const blob = new Blob(chunks, { type: "audio/webm" });

        const wavBlob = await convertToWav(blob);

        const formData = new FormData();
        formData.append("file", wavBlob, "input.wav");

        const res = await fetch(API_URL, {
          method: "POST",
          body: formData,
          credentials: "same-origin"
        });

        if (!res.ok) {
          throw new Error("API failed");
        }

        status.innerText = "Playing response...";

        const audioBlob = await res.blob();
        const url = URL.createObjectURL(audioBlob);

        player.src = url;
        await player.play();

        status.innerText = "Done";

      } catch (err) {
        console.error(err);
        status.innerText = "❌ API / Audio error";
      }
    };

    mediaRecorder.start();
    status.innerText = "🎙️ Recording...";
    btn.innerText = "Stop";

  } catch (err) {
    console.error(err);

    if (!window.isSecureContext) {
      status.innerText = "❌ Mic blocked (secure context required)";
    } else {
      status.innerText = "❌ Mic permission denied";
    }
  }
}

function stopRecording() {
  mediaRecorder.stop();
  btn.innerText = "Start Recording";
  status.innerText = "Uploading...";
}

// 🔥 WEBM → WAV conversion (unchanged)
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

// ----------------------------
// CHAT HISTORY UI (FIXED SCROLL LOGIC ONLY)
// ----------------------------
async function loadChat() {
  try {
    const box = document.getElementById("chatBox");

    // ✅ remember if user was near bottom BEFORE refresh
    const isNearBottom =
      box.scrollHeight - box.scrollTop - box.clientHeight < 60;

    const res = await fetch(window.location.origin + "/chat-history");
    const data = await res.json();

    box.innerHTML = "";

    data.history.forEach(msg => {
      const div = document.createElement("div");

      if (msg.role === "user") {
        div.className = "msg-user";
        div.textContent = "YOU: " + msg.text;
      } else {
        div.className = "msg-ai";
        div.textContent = "AI: " + msg.text;
      }

      box.appendChild(div);
    });

    // ✅ ONLY auto-scroll if user already at bottom
    if (isNearBottom) {
      box.scrollTop = box.scrollHeight;
    }

  } catch (err) {
    console.error("Chat load failed", err);
  }
}

// auto refresh
setInterval(loadChat, 2000);
loadChat();
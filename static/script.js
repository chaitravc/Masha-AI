// static/script.js
document.addEventListener("DOMContentLoaded", () => {
    // Log to confirm the script is loading
    console.log('Masha and the AI Bear script loaded!');

    const recordBtn = document.getElementById("recordBtn");
    const statusDisplay = document.getElementById("statusDisplay");
    const chatLog = document.getElementById('chat-log');

    // Select the modal elements
    const settingsBtn = document.getElementById('settingsBtn');
    const apiModal = document.getElementById('apiModal');
    const closeModalBtn = document.getElementById('closeModalBtn');
    const saveKeysBtn = document.getElementById('saveKeysBtn');
    const geminiKeyInput = document.getElementById('geminiKey');
    const assemblyKeyInput = document.getElementById('assemblyKey');
    const murfKeyInput = document.getElementById('murfKey');
    const keyStatusDisplay = document.getElementById('keyStatus');

    let isRecording = false;
    let ws = null;
    let audioContext;
    let mediaStream;
    let processor;
    let audioQueue = [];
    let isPlaying = false;
    let assistantMessageDiv = null;

    // API Key State Management
    let keys = {
        gemini: localStorage.getItem('GEMINI_API_KEY'),
        assembly: localStorage.getItem('ASSEMBLYAI_API_KEY'),
        murf: localStorage.getItem('MURF_API_KEY')
    };

    const addOrUpdateMessage = (text, type) => {
        if (type === "assistant") {
            if (assistantMessageDiv && chatLog.contains(assistantMessageDiv)) {
                assistantMessageDiv.textContent = text;
            } else {
                assistantMessageDiv = document.createElement('div');
                assistantMessageDiv.className = 'message assistant';
                assistantMessageDiv.textContent = text;
                chatLog.appendChild(assistantMessageDiv);
            }
        } else {
            assistantMessageDiv = null;
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message user';
            messageDiv.textContent = text;
            chatLog.appendChild(messageDiv);
        }
        chatLog.scrollTop = chatLog.scrollHeight;
    };

    const playNextInQueue = () => {
        if (audioQueue.length > 0) {
            isPlaying = true;
            const base64Audio = audioQueue.shift();
            // Create an Audio element
            const audio = new Audio("data:audio/wav;base64," + base64Audio);

            audio.onended = () => {
                isPlaying = false;
                playNextInQueue();
            };
            audio.play().catch(e => console.error("Error playing audio:", e));
        }
    };

    const startRecording = async () => {
        try {
            mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
            audioContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });
            const source = audioContext.createMediaStreamSource(mediaStream);

            processor = audioContext.createScriptProcessor(1024, 1, 1);
            source.connect(processor);
            processor.connect(audioContext.destination);

            // Generate WebSocket URL based on current host
            const wsUrl = `ws://${window.location.host}/ws`;
            ws = new WebSocket(wsUrl);

            ws.onopen = () => {
                console.log("✅ WebSocket connection open");
                // Also send API keys to the backend on open
                ws.send(JSON.stringify({
                    type: 'api_keys',
                    gemini: localStorage.getItem('GEMINI_API_KEY'),
                    assemblyai: localStorage.getItem('ASSEMBLYAI_API_KEY'),
                    murf: localStorage.getItem('MURF_API_KEY')
                }));
            };

            processor.onaudioprocess = (e) => {
                if (ws && ws.readyState === WebSocket.OPEN) {
                    const audioData = e.inputBuffer.getChannelData(0);
                    const pcm16 = new Int16Array(audioData.length);
                    for (let i = 0; i < audioData.length; i++) {
                        pcm16[i] = Math.max(-1, Math.min(1, audioData[i])) * 0x7FFF;
                    }
                    ws.send(pcm16.buffer);
                }
            };

            ws.onclose = () => {
                console.log("⚠️ WebSocket closed");
                stopRecording();
            };

            ws.onerror = (error) => {
                console.error("❌ WebSocket Error:", error);
                stopRecording();
            };

            ws.onmessage = (event) => {
                const msg = JSON.parse(event.data);
                if (msg.type === "partial") {
                    if (assistantMessageDiv) {
                        assistantMessageDiv.textContent = msg.text;
                    } else {
                        addOrUpdateMessage(msg.text, "assistant");
                    }
                } else if (msg.type === "final") {
                    addOrUpdateMessage(msg.text, "user");
                } else if (msg.type === "assistant") {
                    addOrUpdateMessage(msg.text, "assistant");
                } else if (msg.type === "audio") {
                    audioQueue.push(msg.b64);
                    if (!isPlaying) {
                        playNextInQueue();
                    }
                }
            };

            isRecording = true;
            recordBtn.classList.add("recording");
            statusDisplay.textContent = "Listening...";
        } catch (error) {
            console.error("Could not start recording:", error);
            alert("Microphone access is required to use the voice agent.");
        }
    };

    const stopRecording = () => {
        if (processor) processor.disconnect();
        if (mediaStream) mediaStream.getTracks().forEach(track => track.stop());
        if (ws) ws.close();

        isRecording = false;
        recordBtn.classList.remove("recording");
        statusDisplay.textContent = "Ready to chat!";
    };

    recordBtn.addEventListener("click", () => {
        if (isRecording) {
            stopRecording();
        } else {
            startRecording();
        }
    });

    // Modal functionality
    if (settingsBtn && apiModal && closeModalBtn) {
        settingsBtn.addEventListener('click', () => {
            console.log('Settings button clicked. Showing modal.');
            geminiKeyInput.value = keys.gemini || '';
            assemblyKeyInput.value = keys.assembly || '';
            murfKeyInput.value = keys.murf || '';
            apiModal.classList.add('show');
        });

        closeModalBtn.addEventListener('click', () => {
            console.log('Close button clicked. Hiding modal.');
            apiModal.classList.remove('show');
        });

        saveKeysBtn.addEventListener('click', (e) => {
            e.preventDefault();
            keys.gemini = geminiKeyInput.value.trim();
            keys.assembly = assemblyKeyInput.value.trim();
            keys.murf = murfKeyInput.value.trim();

            localStorage.setItem('GEMINI_API_KEY', keys.gemini);
            localStorage.setItem('ASSEMBLYAI_API_KEY', keys.assembly);
            localStorage.setItem('MURF_API_KEY', keys.murf);

            keyStatusDisplay.textContent = 'Keys saved successfully!';
            setTimeout(() => {
                apiModal.classList.remove('show');
                keyStatusDisplay.textContent = '';
            }, 1500);
        });
    } else {
        console.error("Error: Modal elements not found. Please check your HTML IDs.");
    }
});
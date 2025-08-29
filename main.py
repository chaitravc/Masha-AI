# main.py
from fastapi import FastAPI, Request, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import logging
import asyncio
import base64
import re
import json

# Import services and config
import config
from services import stt, llm, tts
# Import the roast-related functions
from services.roast import should_roast_user, format_roast_response

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

# Mount static files for CSS/JS
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def home(request: Request):
    """Serves the main HTML page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Handles WebSocket connection for real-time transcription and voice response."""
    await websocket.accept()
    logging.info("WebSocket client connected.")

    loop = asyncio.get_event_loop()
    chat_history = []
    transcriber = None # Initialize transcriber as None

    async def handle_transcript(text: str):
        """Processes the final transcript, gets LLM and TTS responses, and streams audio."""
        await websocket.send_json({"type": "final", "text": text})
        try:
            # Check if the user's query is a roast request
            roast_info = should_roast_user(text)

            if roast_info["is_roast_request"]:
                # If it's a roast request, get the response from the roast module
                full_response = format_roast_response(roast_info)
                # The chat history is not updated for roasts as they are a special, one-off response
            else:
                # If not a roast, proceed with the normal LLM logic
                full_response, updated_history = llm.get_llm_response(text, chat_history)
                # Update history for the next turn
                chat_history.clear()
                chat_history.extend(updated_history)

            # Send the full text response to the UI
            await websocket.send_json({"type": "assistant", "text": full_response})

            # 2. Split the response into sentences
            sentences = re.split(r'(?<=[.?!])\s+', full_response.strip())

            # 3. Process each sentence for TTS and stream audio back
            for sentence in sentences:
                if sentence.strip():
                    # Run the blocking TTS function in a separate thread
                    audio_bytes = await loop.run_in_executor(
                        None, tts.speak, sentence.strip()
                    )
                    if audio_bytes:
                        b64_audio = base64.b64encode(audio_bytes).decode('utf-8')
                        await websocket.send_json({"type": "audio", "b64": b64_audio})

        except Exception as e:
            logging.error(f"Error in LLM/TTS pipeline: {e}")
            # The error message should also be in character now
            await websocket.send_json({"type": "llm", "text": "Oh honey, my brain's a bit fried. What were you saying?"})

    def on_final_transcript(text: str):
        logging.info(f"Final transcript received: {text}")
        asyncio.run_coroutine_threadsafe(handle_transcript(text), loop)

    try:
        while True:
            data = await websocket.receive()
            if data["type"] == "websocket.receive" and "text" in data:
                message = json.loads(data["text"])
                if message.get("type") == "api_keys":
                    logging.info("Received API keys from frontend, updating configuration.")
                    config.set_api_keys(
                        gemini_key=message.get("gemini"),
                        assemblyai_key=message.get("assemblyai"),
                        murf_key=message.get("murf")
                    )
                    # Re-initialize transcriber with new key
                    if transcriber:
                        transcriber.close()
                    # CRITICAL FIX: The transcriber is now created only after the API key is received.
                    transcriber = stt.AssemblyAIStreamingTranscriber(
                        api_key=config.ASSEMBLYAI_API_KEY,
                        on_final_callback=on_final_transcript
                    )
                else:
                    # This case handles a text message that is not an API key update,
                    # which is not expected but good to have.
                    logging.info("Received an unexpected text message.")

            else:
                # Assume it's audio data if transcriber is ready
                if transcriber:
                    transcriber.stream_audio(data["bytes"])
    except Exception as e:
        logging.info(f"WebSocket connection closed: {e}")
    finally:
        if transcriber:
            transcriber.close()
        logging.info("Transcription resources released.")
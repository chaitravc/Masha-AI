# services/stt.py
import assemblyai as aai
from fastapi import UploadFile
import os
from dotenv import load_dotenv
from assemblyai.streaming.v3 import (
    StreamingClient,
    StreamingClientOptions,
    StreamingParameters,
    StreamingSessionParameters,
    StreamingEvents,
    BeginEvent,
    TurnEvent,
    TerminationEvent,
    StreamingError,
)

# Import the config module to get the API key
import config

load_dotenv()

# expects ASSEMBLYAI_API_KEY in env
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY") or ""


class AssemblyAIStreamingTranscriber:
    """
    Wrapper around AAI StreamingClient that exposes:
      - on_partial_callback(text) for interim results
      - on_final_callback(text)   when end_of_turn=True
    """

    def __init__(
            self,
            api_key: str,
            sample_rate: int = 16000,
            on_partial_callback=None,
            on_final_callback=None,
    ):
        self.on_partial_callback = on_partial_callback
        self.on_final_callback = on_final_callback

        options = StreamingClientOptions(
            token_auth=False,
            api_key=api_key,
        )

        self.client = StreamingClient(options=options)

        # FIX: The on_begin, on_termination, and on_error callbacks are now set using the .on() method
        self.client.on(StreamingEvents.Begin, self._on_begin)
        self.client.on(StreamingEvents.Termination, self._on_termination)
        self.client.on(StreamingEvents.Error, self._on_error)

        self.client.on(
            StreamingEvents.Turn,
            lambda client, event: self._on_turn(client, event),
        )

        self.client.connect(
            StreamingParameters(
                sample_rate=sample_rate,
                format_turns=False,
            )
        )

    # Corrected method signatures to include 'self'
    def _on_begin(self, client: StreamingClient, event: BeginEvent):
        print(f"AAI session started: {event.id}")

    # Corrected method signatures to include 'self'
    def _on_termination(self, client: StreamingClient, event: TerminationEvent):
        print(f"AAI session terminated after {event.audio_duration_seconds} s")

    # Corrected method signatures to include 'self'
    def _on_error(self, client: StreamingClient, error: StreamingError):
        print("AAI error:", error)

    def _on_turn(self, client: StreamingClient, event: TurnEvent):
        text = (event.transcript or "").strip()
        if not text:
            return

        if event.end_of_turn:
            if self.on_final_callback:
                self.on_final_callback(text)

            if not event.turn_is_formatted:
                try:
                    client.set_params(StreamingSessionParameters(format_turns=True))
                except Exception as set_err:
                    print("set_params error:", set_err)
        else:
            if self.on_partial_callback:
                self.on_partial_callback(text)

    def stream_audio(self, audio_chunk: bytes):
        self.client.stream(audio_chunk)

    def close(self):
        self.client.disconnect(terminate=True)


def transcribe_audio(audio_file: UploadFile) -> str:
    """Transcribes audio to text using AssemblyAI."""
    # This function is not used in the streaming flow but is kept for completeness.
    # It also needs the API key to be passed.
    transcriber = aai.Transcriber(api_key=os.getenv("ASSEMBLYAI_API_KEY"))
    transcript = transcriber.transcribe(audio_file.file)

    if transcript.status:
        return transcript.text
    return ""
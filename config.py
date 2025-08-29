# config.py
import os
from dotenv import load_dotenv
import assemblyai as aai
import google.generativeai as genai
import logging
import murf

# Global variables for keys
MURF_API_KEY = None
ASSEMBLYAI_API_KEY = None
GEMINI_API_KEY = None
TAVILY_API_KEY = None
NEWS_API_KEY = None

# Load environment variables from .env file
load_dotenv()


# --- Functions to manage API keys ---
def set_api_keys(gemini_key=None, assemblyai_key=None, murf_key=None):
    """
    Sets global API keys. Prioritizes provided keys, falls back to .env file.
    """
    global GEMINI_API_KEY, ASSEMBLYAI_API_KEY, MURF_API_KEY

    # Use provided keys if available, otherwise fall back to .env
    GEMINI_API_KEY = gemini_key or os.getenv("GEMINI_API_KEY")
    ASSEMBLYAI_API_KEY = assemblyai_key or os.getenv("ASSEMBLYAI_API_KEY")
    MURF_API_KEY = murf_key or os.getenv("MURF_API_KEY")

    # Configure APIs and log warnings
    if ASSEMBLYAI_API_KEY:
        aai.settings.api_key = ASSEMBLYAI_API_KEY
    else:
        logging.warning("ASSEMBLYAI_API_KEY not found. Please provide it via the UI or .env file.")

    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
    else:
        logging.warning("GEMINI_API_KEY not found. Please provide it via the UI or .env file.")

    if not MURF_API_KEY:
        logging.warning("MURF_API_KEY not found. Please provide it via the UI or .env file.")


# Set initial keys from .env on startup
set_api_keys()

# Load other non-user-configurable keys from .env
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
# Masha AI 



Meet **Masha AI** – a fun, Masha and the Bear–themed conversational AI voice agent that listens, understands, and responds to you in real-time, both in **text** and **voice** form.  

The persona of the agent is **Masha**, the mischievous little character from the cartoon *Masha and the Bear*.  
When you click the 🎙️ mic button, you can talk to her directly, and she will respond in her unique voice and personality.  

---


##  Task Overview
- Updated the README.md with **newly added features**  
- Documented integration of:  
  - **News API** – delivers trending news in a funny “Masha-style” narration  
  - **Roast Mode** – when triggered by keywords like *roast, roast yourself, make fun*, Masha responds with a witty roasted reply  
- Ensured clear explanation of client-side and server-side functionality  
- Extended dependency list to include **News API** integration  

---

##  How It Works

###  Client Side
- Clicks mic button to record audio  
- Streams audio chunks to the server using **WebSockets**  
- Displays the response in **text form**  
- Plays back the response in **voice form** in real time  

###  Server Side
- Receives and buffers audio chunks from client  
- Sends audio to **AssemblyAI** for transcription (STT)  
- Passes transcribed text to **Google Gemini LLM** to generate response  
- Stores conversation history for context retention  
- Converts response text into speech using **Murf AI**  
- Detects **roast trigger words** (like “roast yourself” / “make fun of yourself”) and switches to roast mode  
- Fetches **news updates** via **News API** and delivers them in a funny, playful style  

---

##  Tech Stack
- **Frontend:** HTML, CSS, JavaScript (recording, streaming, audio playback)  
- **Backend:** Python (FastAPI)  
- **APIs:**  
  - AssemblyAI (Speech-to-Text)  
  - Google Gemini (LLM)  
  - Murf AI (Text-to-Speech)  
  - News API (funny news updates)  
- **Communication:** WebSockets  
- **Runtime:** Uvicorn  

---




##  Project Structure

```bash
Masha-AI/
├── Lib/                   # Virtual environment libraries
├── Scripts/               # Virtual environment scripts
├── services/              # Core backend logic
│ ├── init.py
│ ├── llm.py               # Handles LLM (Google Gemini) logic
│ ├── news.py              # Fetches and formats news (funny narration)
│ ├── roast.py             # Roast mode responses
│ ├── stt.py               # Speech-to-Text using AssemblyAI
│ └── tts.py               # Text-to-Speech using Murf AI
│
├── static/                # Static frontend assets
│ ├── fallback.mp3         # Default fallback audio
│ ├── m.jpg                # Image asset
│ ├── mab.jpg              # Image asset
│ ├── masha.jpg            # Masha theme image
│ ├── script.js            # Frontend JS (mic, streaming, API calls)
│ └── style.css            # Frontend styling
│
├── templates/             # HTML templates
│ └── index.html           # Main frontend interface
│
├── uploads/               # (Optional) Uploads directory
│
├── .env                   # Environment variables (API keys)
├── config.py              # App configuration
├── main.py                # FastAPI entry point
├── requirements.txt       # Python dependencies
├── schemas.py             # Data models/schemas
└── .gitignore             # Git ignore file
````


##  Setup Instructions

###  Clone Repository
```bash
git clone https://github.com/chaitravc/masha-ai.git
cd masha-ai
````

###  Install Dependencies

```bash
pip install -r requirements.txt
```

###  Run Server Locally

```bash
uvicorn main:app --reload
```

### Test the Agent

1. Open the frontend in your browser
2. Click on the 🎙️ mic button and speak into the microphone
3. Your voice will be **transcribed to text**
4. The **LLM will generate a response**
5. The response will be:

   * **Normal conversation** (default)
   * **Roast Mode** if roast triggers are detected
   * **Funny News Headlines** if user asks for “news”
6. The response will be **spoken back to you in real time** with Murf AI

---

##  Dependencies

* fastapi
* uvicorn
* websockets
* requests
* murf
* assemblyai
* tavily-python
* newsapi-python

---

##  Output

A working **end-to-end conversational Masha-themed AI voice agent** with extended features:

* **Talk to Masha** in real-time
* **Get funny news updates**
* **Get roasted by Masha** when you dare to ask 

---


 *Masha is ready to chat, roast, and deliver the news in her own funny way!*





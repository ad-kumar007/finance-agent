import os
import uuid
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agents.language_agent import answer_question
from orchestrator.voice_agent import speech_to_text, text_to_speech  # helper functions
from orchestrator.fallback_handler import fallback_handler, handle_exception
import traceback  # For better error logging
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Orchestrator")

app = FastAPI(
    title="Finance Assistant API",
    description="Multi-Agent Finance Assistant with voice support",
    version="1.0.0"
)

# Add CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=False,  # Must be False when using wildcard
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Finance Assistant Orchestrator"}

# Create directory to store audio responses
AUDIO_DIR = "audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

# ---------------------- TEXT LLM ENDPOINT ----------------------

class Question(BaseModel):
    question: str

@app.post("/ask_llm")
async def ask_llm(data: Question):
    """
    Answer a text question using RAG and LLM.
    """
    try:
        logger.info(f"Processing question: {data.question[:100]}")
        answer = answer_question(data.question)
        logger.info("Successfully generated answer")
        return {
            "question": data.question,
            "answer": answer
        }
    except Exception as e:
        logger.error(f"Error in ask_llm: {e}")
        traceback.print_exc()
        fallback = handle_exception("language_agent", data.question, e)
        return {"error": fallback["message"], "suggestions": fallback.get("suggestions", [])}

# ---------------------- AUDIO ENDPOINTS ----------------------

@app.post("/ask_audio")
async def ask_audio(audio_file: UploadFile = File(...)):
    try:
        # Save uploaded audio temporarily
        temp_path = f"temp_{uuid.uuid4().hex}.wav"
        with open(temp_path, "wb") as f:
            content = await audio_file.read()
            f.write(content)
        
        # Convert audio to text
        question = speech_to_text(temp_path)
        os.remove(temp_path)
        
        # Get answer from language agent
        answer = answer_question(question)
        
        # Convert answer text to speech
        output_filename = f"{uuid.uuid4().hex}.mp3"
        output_filepath = os.path.join(AUDIO_DIR, output_filename)
        text_to_speech(answer, output_filepath)
        
        return {
            "question": question,
            "answer": answer,
            "answer_audio_file": output_filename
        }
    except Exception as e:
        traceback.print_exc()
        return {"error": str(e)}

@app.get("/audio/{filename}")
async def get_audio(filename: str):
    file_path = os.path.join(AUDIO_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="audio/mpeg")
    return {"error": "Audio not found."}

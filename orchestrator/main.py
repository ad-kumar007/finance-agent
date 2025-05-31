import os
import uuid
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel
from agents.language_agent import answer_question
from orchestrator.voice_agent import speech_to_text, text_to_speech  # helper functions
import traceback  # For better error logging

app = FastAPI()

# Create directory to store audio responses
AUDIO_DIR = "audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

# ---------------------- TEXT LLM ENDPOINT ----------------------

class Question(BaseModel):
    question: str

@app.post("/ask_llm")
async def ask_llm(data: Question):
    try:
        answer = answer_question(data.question)
        return {
            "question": data.question,
            "answer": answer
        }
    except Exception as e:
        traceback.print_exc()
        return {"error": str(e)}

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

import os
import uuid
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel

from agents.language_agent import answer_question
from orchestrator.voice_agent import speech_to_text, text_to_speech

app = FastAPI()

AUDIO_DIR = "audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

# ✅ Text-based LLM Question
class Question(BaseModel):
    question: str

@app.post("/ask_llm")
async def ask_llm(data: Question):
    answer = answer_question(data.question)
    return {
        "question": data.question,
        "answer": answer
    }

# ✅ Voice-based Question
@app.post("/ask_audio")
async def ask_audio(audio_file: UploadFile = File(...)):
    temp_path = f"temp_{uuid.uuid4().hex}.wav"
    with open(temp_path, "wb") as f:
        content = await audio_file.read()
        f.write(content)

    question = speech_to_text(temp_path)
    os.remove(temp_path)

    answer = answer_question(question)

    output_filename = f"{uuid.uuid4().hex}.mp3"
    output_filepath = os.path.join(AUDIO_DIR, output_filename)
    text_to_speech(answer, output_filepath)

    return {
        "question": question,
        "answer": answer,
        "answer_audio_file": output_filename
    }

# ✅ Serve the generated MP3 file
@app.get("/audio/{filename}")
async def get_audio(filename: str):
    file_path = os.path.join(AUDIO_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="audio/mpeg")
    return {"error": "Audio not found."}

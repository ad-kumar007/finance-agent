import whisper
import pyttsx3

# Initialize Whisper model once
model = whisper.load_model("base")

def speech_to_text(audio_path: str) -> str:
    """
    Use Whisper ASR to transcribe audio file to text.
    """
    result = model.transcribe(audio_path)
    return result["text"]

def text_to_speech(text: str, output_path: str):
    """
    Use pyttsx3 to synthesize speech from text and save to mp3.
    """
    engine = pyttsx3.init()
    engine.save_to_file(text, output_path)
    engine.runAndWait()

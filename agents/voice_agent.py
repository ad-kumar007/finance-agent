# agents/voice_agent.py

import os
import openai
from pydub import AudioSegment
from pydub.playback import play
from gtts import gTTS  # Google Text-to-Speech library for TTS

# Load your OpenRouter API key from environment variables
openai.api_key = os.getenv("OPENROUTER_API_KEY")

def speech_to_text(audio_file_path: str) -> str:
    """
    Converts speech in an audio file to text using OpenAI Whisper API.

    Args:
        audio_file_path (str): Path to the audio file (wav, mp3, etc.)

    Returns:
        str: Transcribed text from audio
    """
    with open(audio_file_path, "rb") as audio_file:
        # Call Whisper API to transcribe audio
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
    
    return transcript['text']


def text_to_speech(text: str, output_path="output.mp3"):
    """
    Converts text to speech and plays the audio.

    Args:
        text (str): Text to convert to speech
        output_path (str): Path to save temporary audio file (default "output.mp3")
    """
    # Convert text to speech using Google Text-to-Speech
    tts = gTTS(text)
    tts.save(output_path)

    # Load the audio and play it
    audio = AudioSegment.from_file(output_path)
    play(audio)


# Simple test routine if running this script directly
if __name__ == "__main__":
    print("Please record your question as 'question.wav' in this folder.")
    question_text = speech_to_text("question.wav")
    print("You asked:", question_text)

    # Example response - replace this with your answer_question function output
    example_answer = "TSMC beat earnings expectations with an EPS of 2.01 dollars."
    print("Answer:", example_answer)

    # Speak out the answer
    text_to_speech(example_answer)

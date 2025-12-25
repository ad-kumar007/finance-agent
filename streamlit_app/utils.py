# streamlit_app/utils.py
"""
Utility functions for the Streamlit Finance Assistant app.
Provides API helpers, audio validation, formatting, and session management.
"""

import os
import tempfile
import mimetypes
from typing import Optional, Dict, Any, Tuple
import requests
from datetime import datetime


# API Configuration
DEFAULT_API_BASE_URL = "http://localhost:8001"


class APIClient:
    """
    HTTP client for communicating with the FastAPI backend.
    """
    
    def __init__(self, base_url: str = DEFAULT_API_BASE_URL, timeout: int = 30):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL of the FastAPI backend
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
    
    def ask_text(self, question: str) -> Dict[str, Any]:
        """
        Send a text question to the LLM endpoint.
        
        Args:
            question: The user's question
        
        Returns:
            Dict with 'question', 'answer', or 'error'
        """
        try:
            response = requests.post(
                f"{self.base_url}/ask_llm",
                json={"question": question},
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            return {"error": "Request timed out. Please try again."}
        except requests.exceptions.ConnectionError:
            return {"error": "Could not connect to the server. Is the backend running?"}
        except Exception as e:
            return {"error": str(e)}
    
    def ask_audio(self, audio_file_path: str, filename: str) -> Dict[str, Any]:
        """
        Send an audio file to the audio endpoint.
        
        Args:
            audio_file_path: Path to the audio file
            filename: Original filename
        
        Returns:
            Dict with 'question', 'answer', 'answer_audio_file', or 'error'
        """
        try:
            with open(audio_file_path, "rb") as f:
                files = {"audio_file": (filename, f)}
                response = requests.post(
                    f"{self.base_url}/ask_audio",
                    files=files,
                    timeout=self.timeout
                )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            return {"error": "Audio processing timed out. Try a shorter recording."}
        except requests.exceptions.ConnectionError:
            return {"error": "Could not connect to the server. Is the backend running?"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_audio_file(self, filename: str) -> Optional[bytes]:
        """
        Retrieve an audio file from the server.
        
        Args:
            filename: Name of the audio file
        
        Returns:
            Audio file bytes or None if not found
        """
        try:
            response = requests.get(
                f"{self.base_url}/audio/{filename}",
                timeout=self.timeout
            )
            if response.status_code == 200:
                return response.content
            return None
        except Exception:
            return None
    
    def health_check(self) -> bool:
        """
        Check if the backend is responsive.
        
        Returns:
            True if backend is healthy, False otherwise
        """
        try:
            response = requests.get(
                f"{self.base_url}/",
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False


# Audio file utilities

ALLOWED_AUDIO_EXTENSIONS = {'.wav', '.mp3', '.m4a', '.ogg', '.flac', '.webm'}
MAX_AUDIO_SIZE_MB = 25


def validate_audio_file(file) -> Tuple[bool, str]:
    """
    Validate an uploaded audio file.
    
    Args:
        file: Streamlit UploadedFile object
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if file is None:
        return False, "No file uploaded"
    
    # Check file extension
    filename = file.name.lower()
    ext = os.path.splitext(filename)[1]
    if ext not in ALLOWED_AUDIO_EXTENSIONS:
        return False, f"Unsupported file type. Allowed: {', '.join(ALLOWED_AUDIO_EXTENSIONS)}"
    
    # Check file size
    file.seek(0, 2)  # Seek to end
    size_mb = file.tell() / (1024 * 1024)
    file.seek(0)  # Reset to beginning
    
    if size_mb > MAX_AUDIO_SIZE_MB:
        return False, f"File too large. Maximum size: {MAX_AUDIO_SIZE_MB} MB"
    
    if size_mb == 0:
        return False, "File is empty"
    
    return True, ""


def save_temp_audio(file) -> Tuple[Optional[str], str]:
    """
    Save an uploaded audio file to a temporary location.
    
    Args:
        file: Streamlit UploadedFile object
    
    Returns:
        Tuple of (temp_file_path, error_message)
    """
    try:
        ext = os.path.splitext(file.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(file.read())
            return tmp.name, ""
    except Exception as e:
        return None, f"Failed to save audio file: {e}"


def cleanup_temp_file(file_path: Optional[str]) -> None:
    """
    Clean up a temporary file.
    
    Args:
        file_path: Path to the temporary file
    """
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception:
            pass  # Ignore cleanup errors


def get_audio_mime_type(filename: str) -> str:
    """
    Get the MIME type for an audio file.
    
    Args:
        filename: Name of the audio file
    
    Returns:
        MIME type string
    """
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or "audio/mpeg"


# Response formatting utilities

def format_answer_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format and validate an answer response from the API.
    
    Args:
        data: Raw response data from API
    
    Returns:
        Formatted response dict
    """
    if "error" in data:
        return {
            "success": False,
            "error": data["error"]
        }
    
    if "question" in data and "answer" in data:
        return {
            "success": True,
            "question": data["question"],
            "answer": data["answer"],
            "audio_file": data.get("answer_audio_file")
        }
    
    return {
        "success": False,
        "error": "Unexpected response format from server"
    }


def truncate_text(text: str, max_length: int = 500) -> str:
    """
    Truncate text to a maximum length with ellipsis.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
    
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def format_timestamp() -> str:
    """Get a formatted timestamp string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# Session state helpers

class SessionState:
    """
    Helper class for managing Streamlit session state.
    """
    
    @staticmethod
    def init_defaults(st_session_state) -> None:
        """
        Initialize default session state values.
        
        Args:
            st_session_state: Streamlit session_state object
        """
        defaults = {
            "chat_history": [],
            "last_question": "",
            "last_answer": "",
            "api_client": None,
            "is_processing": False,
            "error_count": 0
        }
        
        for key, value in defaults.items():
            if key not in st_session_state:
                st_session_state[key] = value
    
    @staticmethod
    def add_to_history(st_session_state, question: str, answer: str) -> None:
        """
        Add a Q&A pair to chat history.
        
        Args:
            st_session_state: Streamlit session_state object
            question: User's question
            answer: Agent's answer
        """
        st_session_state.chat_history.append({
            "timestamp": format_timestamp(),
            "question": question,
            "answer": answer
        })
        st_session_state.last_question = question
        st_session_state.last_answer = answer
    
    @staticmethod
    def clear_history(st_session_state) -> None:
        """
        Clear chat history.
        
        Args:
            st_session_state: Streamlit session_state object
        """
        st_session_state.chat_history = []
        st_session_state.last_question = ""
        st_session_state.last_answer = ""
    
    @staticmethod
    def get_api_client(st_session_state, base_url: str = DEFAULT_API_BASE_URL) -> APIClient:
        """
        Get or create an API client from session state.
        
        Args:
            st_session_state: Streamlit session_state object
            base_url: API base URL
        
        Returns:
            APIClient instance
        """
        if st_session_state.api_client is None:
            st_session_state.api_client = APIClient(base_url)
        return st_session_state.api_client


# Example questions for the UI
EXAMPLE_QUESTIONS = [
    "What's our risk exposure in Asia tech stocks today?",
    "Did TSMC beat earnings expectations?",
    "What is the current RSI for Apple stock?",
    "Highlight any earnings surprises in the semiconductor sector",
    "Give me a market briefing for today"
]


def get_example_questions() -> list:
    """Get a list of example questions for the UI."""
    return EXAMPLE_QUESTIONS.copy()


# Test routine
if __name__ == "__main__":
    print("Testing Streamlit Utils...")
    
    # Test API client
    print("\n=== API Client ===")
    client = APIClient()
    print(f"Base URL: {client.base_url}")
    print(f"Health Check: {client.health_check()}")
    
    # Test audio validation
    print("\n=== Audio Validation ===")
    print(f"Allowed extensions: {ALLOWED_AUDIO_EXTENSIONS}")
    print(f"Max size: {MAX_AUDIO_SIZE_MB} MB")
    
    # Test formatting
    print("\n=== Text Formatting ===")
    long_text = "This is a very long text that should be truncated. " * 20
    print(f"Truncated: {truncate_text(long_text, 50)}")
    
    # Test example questions
    print("\n=== Example Questions ===")
    for q in get_example_questions()[:3]:
        print(f"  - {q}")

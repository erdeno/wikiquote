import whisper
import torch
import tempfile
import os
from typing import Optional

class WhisperASR:
    def __init__(self, model_size: str = "base"):
        """
        Initialize Whisper ASR
        Args:
            model_size: tiny, base, small, medium, large
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading Whisper model '{model_size}' on {self.device}...")
        self.model = whisper.load_model(model_size, device=self.device)
        print("Whisper model loaded successfully.")
    
    def transcribe(self, audio_file_path: str, language: Optional[str] = None) -> dict:
        """
        Transcribe audio file to text
        """
        options = {}
        if language:
            options['language'] = language
        
        result = self.model.transcribe(audio_file_path, **options)
        
        return {
            'text': result['text'].strip(),
            'language': result.get('language', 'unknown'),
            'segments': result.get('segments', [])
        }
    
    def transcribe_bytes(self, audio_bytes: bytes, language: Optional[str] = None) -> dict:
        """
        Transcribe audio from bytes
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_path = tmp_file.name
        
        try:
            result = self.transcribe(tmp_path, language)
        finally:
            os.unlink(tmp_path)
        
        return result
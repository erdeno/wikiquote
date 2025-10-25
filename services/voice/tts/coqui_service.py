from TTS.api import TTS
import torch
import tempfile
import os
from typing import Optional
import json

class CoquiTTS:
    """
    Text-to-Speech using Coqui TTS
    """
    
    def __init__(self, model_name: str = "tts_models/en/ljspeech/tacotron2-DDC"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading TTS model '{model_name}' on {self.device}...")
        
        self.tts = TTS(model_name).to(self.device)
        
        # User TTS preferences
        self.user_preferences: dict = {}
        self.preferences_file = "tts_preferences.json"
        self._load_preferences()
        
        print("TTS model loaded successfully.")
    
    def _load_preferences(self):
        """Load user TTS preferences"""
        if os.path.exists(self.preferences_file):
            try:
                with open(self.preferences_file, 'r') as f:
                    self.user_preferences = json.load(f)
            except Exception as e:
                print(f"Error loading preferences: {e}")
    
    def _save_preferences(self):
        """Save user TTS preferences"""
        try:
            with open(self.preferences_file, 'w') as f:
                json.dump(self.user_preferences, f, indent=2)
        except Exception as e:
            print(f"Error saving preferences: {e}")
    
    def set_user_preferences(self, speaker_id: str, pitch: float = 1.0, 
                           speed: float = 1.0, energy: float = 1.0):
        """Set TTS preferences for a user"""
        self.user_preferences[speaker_id] = {
            'pitch': pitch,
            'speed': speed,
            'energy': energy
        }
        self._save_preferences()
    
    def synthesize_to_file(self, text: str, output_path: str, 
                          speaker: Optional[str] = None) -> bool:
        """Synthesize text to audio file"""
        try:
            if speaker and self.tts.is_multi_speaker:
                self.tts.tts_to_file(text=text, file_path=output_path, speaker=speaker)
            else:
                self.tts.tts_to_file(text=text, file_path=output_path)
            return True
        except Exception as e:
            print(f"TTS synthesis failed: {e}")
            return False
    
    def synthesize_to_bytes(self, text: str, speaker_id: Optional[str] = None) -> Optional[bytes]:
        """Synthesize text and return audio as bytes"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            success = self.synthesize_to_file(text, tmp_path, speaker_id)
            if success:
                with open(tmp_path, 'rb') as f:
                    audio_bytes = f.read()
                return audio_bytes
            return None
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def get_user_preferences(self, speaker_id: str) -> Optional[dict]:
        """Get TTS preferences for a user"""
        return self.user_preferences.get(speaker_id)
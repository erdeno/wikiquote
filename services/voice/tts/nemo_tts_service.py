import nemo.collections.tts as nemo_tts
import torch
import soundfile as sf
import numpy as np
from typing import Optional, Dict
import tempfile
import os

class NeMoTTS:
    """
    Text-to-Speech using NeMo models
    """
    
    def __init__(self, model_type: str = "fastpitch_hifigan"):
        """
        Initialize NeMo TTS
        
        Args:
            model_type: 'fastpitch_hifigan', 'tacotron2', or 'fastpitch_hifigan_multi'
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading NeMo TTS model '{model_type}' on {self.device}...")
        
        self.model_type = model_type
        
        if model_type == "fastpitch_hifigan":
            # Load FastPitch + HiFiGAN (single speaker, high quality)
            self.spec_generator = nemo_tts.models.FastPitchModel.from_pretrained(
                "nvidia/tts_en_fastpitch"
            )
            self.vocoder = nemo_tts.models.HifiGanModel.from_pretrained(
                "nvidia/tts_hifigan"
            )
            self.is_multi_speaker = False
            
        elif model_type == "fastpitch_hifigan_multi":
            # Multi-speaker model
            self.spec_generator = nemo_tts.models.FastPitchModel.from_pretrained(
                "nvidia/tts_en_fastpitch_multispeaker"
            )
            self.vocoder = nemo_tts.models.HifiGanModel.from_pretrained(
                "nvidia/tts_hifigan"
            )
            self.is_multi_speaker = True
            
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        self.spec_generator = self.spec_generator.to(self.device)
        self.vocoder = self.vocoder.to(self.device)
        self.spec_generator.eval()
        self.vocoder.eval()
        
        # User TTS preferences (maps speaker_id to preferences)
        self.user_preferences: Dict[str, Dict] = {}
        self.preferences_file = "tts_preferences.json"
        
        self._load_preferences()
        
        print("NeMo TTS models loaded successfully.")
    
    def _load_preferences(self):
        """Load user TTS preferences"""
        if os.path.exists(self.preferences_file):
            try:
                import json
                with open(self.preferences_file, 'r') as f:
                    self.user_preferences = json.load(f)
                print(f"Loaded TTS preferences for {len(self.user_preferences)} users")
            except Exception as e:
                print(f"Error loading preferences: {e}")
    
    def _save_preferences(self):
        """Save user TTS preferences"""
        try:
            import json
            with open(self.preferences_file, 'w') as f:
                json.dump(self.user_preferences, f, indent=2)
        except Exception as e:
            print(f"Error saving preferences: {e}")
    
    def set_user_preferences(
        self, 
        speaker_id: str, 
        pitch: float = 1.0,
        speed: float = 1.0,
        energy: float = 1.0
    ):
        """
        Set TTS preferences for a user
        
        Args:
            speaker_id: User identifier
            pitch: Pitch modification (0.5-2.0, default 1.0)
            speed: Speed modification (0.5-2.0, default 1.0)
            energy: Energy/volume (0.5-2.0, default 1.0)
        """
        self.user_preferences[speaker_id] = {
            'pitch': pitch,
            'speed': speed,
            'energy': energy
        }
        self._save_preferences()
        print(f"✓ Set TTS preferences for {speaker_id}")
    
    def synthesize(
        self,
        text: str,
        speaker_id: Optional[str] = None,
        pitch: Optional[float] = None,
        speed: Optional[float] = None,
        energy: Optional[float] = None
    ) -> np.ndarray:
        """
        Synthesize speech from text
        
        Args:
            text: Text to synthesize
            speaker_id: If provided, use stored preferences
            pitch: Pitch modification (overrides stored)
            speed: Speed modification (overrides stored)
            energy: Energy modification (overrides stored)
            
        Returns:
            Audio as numpy array
        """
        # Get user preferences if available
        if speaker_id and speaker_id in self.user_preferences:
            prefs = self.user_preferences[speaker_id]
            pitch = pitch or prefs.get('pitch', 1.0)
            speed = speed or prefs.get('speed', 1.0)
            energy = energy or prefs.get('energy', 1.0)
        else:
            pitch = pitch or 1.0
            speed = speed or 1.0
            energy = energy or 1.0
        
        with torch.no_grad():
            # Parse text
            parsed = self.spec_generator.parse(text)
            
            # Generate spectrogram with modifications
            spectrogram = self.spec_generator.generate_spectrogram(
                tokens=parsed,
                pace=1.0 / speed,  # Inverse for speed
                pitch_shift=pitch - 1.0  # Shift from baseline
            )
            
            # Apply energy modification
            if energy != 1.0:
                spectrogram = spectrogram * energy
            
            # Generate audio from spectrogram
            audio = self.vocoder.convert_spectrogram_to_audio(spec=spectrogram)
            
            # Convert to numpy
            if isinstance(audio, torch.Tensor):
                audio = audio.cpu().numpy()
            
            # Flatten if needed
            if len(audio.shape) > 1:
                audio = audio.flatten()
        
        return audio
    
    def synthesize_to_file(
        self,
        text: str,
        output_path: str,
        speaker_id: Optional[str] = None,
        **kwargs
    ) -> bool:
        """
        Synthesize text and save to file
        
        Args:
            text: Text to synthesize
            output_path: Output WAV file path
            speaker_id: User identifier for preferences
            **kwargs: Additional parameters (pitch, speed, energy)
            
        Returns:
            True if successful
        """
        try:
            audio = self.synthesize(text, speaker_id, **kwargs)
            
            # Save as WAV file (22050 Hz is NeMo default)
            sf.write(output_path, audio, 22050)
            
            return True
        except Exception as e:
            print(f"TTS synthesis failed: {e}")
            return False
    
    def synthesize_to_bytes(
        self,
        text: str,
        speaker_id: Optional[str] = None,
        **kwargs
    ) -> Optional[bytes]:
        """
        Synthesize text and return as bytes
        
        Args:
            text: Text to synthesize
            speaker_id: User identifier for preferences
            **kwargs: Additional parameters
            
        Returns:
            Audio data as bytes
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            success = self.synthesize_to_file(text, tmp_path, speaker_id, **kwargs)
            
            if success:
                with open(tmp_path, 'rb') as f:
                    audio_bytes = f.read()
                return audio_bytes
            return None
            
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def get_user_preferences(self, speaker_id: str) -> Optional[Dict]:
        """Get TTS preferences for a user"""
        return self.user_preferences.get(speaker_id)
    
    def list_users_with_preferences(self) -> list:
        """List all users with TTS preferences"""
        return list(self.user_preferences.keys())

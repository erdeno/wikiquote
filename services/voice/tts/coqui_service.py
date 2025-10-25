from TTS.api import TTS
import torch
import tempfile
import os
from typing import Optional, List, Dict
import json

class CoquiTTS:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"🔊 Initializing TTS on {self.device}...")

        # User TTS preferences
        self.user_preferences: dict = {}
        self.preferences_file = "tts_preferences.json"
        self._load_preferences()
        
        # Try XTTS v2 (most advanced multi-speaker)
        try:
            print("Attempting to load XTTS v2...")
            self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=(self.device=="cuda"))
            self.model_name = "xtts_v2"
            self.is_multi_speaker = True
            
            # XTTS uses different approach - clone from reference audio
            self.voice_presets = {
                'male_1': 'male_1_ref.wav',
                'male_2': 'male_2_ref.wav',
                'male_3': 'male_3_ref.wav',
                'female_1': 'female_1_ref.wav',
                'female_2': 'female_2_ref.wav',
                'female_3': 'female_3_ref.wav',
            }
            
            print(f"✓ Loaded XTTS v2 (voice cloning model)")
            
        except Exception as e:
            print(f"✗ XTTS v2 failed: {e}")
            # Fallback to VCTK
            self._load_vctk()
    
    def _load_vctk(self):
        """Load VCTK as fallback"""
        try:
            print("Loading VCTK VITS...")
            self.tts = TTS("tts_models/en/vctk/vits", gpu=False)
            self.model_name = "vctk"
            self.is_multi_speaker = True
            
            # Map to actual VCTK speaker IDs
            self.voice_presets = {
                'male_1': 'p226',
                'male_2': 'p227', 
                'male_3': 'p232',
                'female_1': 'p225',
                'female_2': 'p228',
                'female_3': 'p229',
            }
            
            print(f"✓ Loaded VCTK with speakers: {list(self.voice_presets.values())}")
            
        except Exception as e:
            print(f"✗ VCTK failed: {e}")
            self._load_fallback()
    
    def _load_fallback(self):
        """Single speaker fallback"""
        print("⚠ Loading single-speaker fallback...")
        self.tts = TTS("tts_models/en/ljspeech/tacotron2-DDC", gpu=False)
        self.model_name = "ljspeech"
        self.is_multi_speaker = False
        self.voice_presets = {}
    
    def _load_preferences(self):
        """Load user TTS preferences"""
        if os.path.exists(self.preferences_file):
            try:
                with open(self.preferences_file, 'r') as f:
                    self.user_preferences = json.load(f)
                print(f"Loaded TTS preferences for {len(self.user_preferences)} users")
            except Exception as e:
                print(f"Error loading preferences: {e}")
    
    def _save_preferences(self):
        """Save user TTS preferences"""
        try:
            with open(self.preferences_file, 'w') as f:
                json.dump(self.user_preferences, f, indent=2)
        except Exception as e:
            print(f"Error saving preferences: {e}")
    
    def set_user_preferences(self, speaker_id: str, voice_type: str = 'female_1',
                           pitch: float = 1.0, speed: float = 1.0, energy: float = 1.0):
        """Set TTS preferences for a user"""
        self.user_preferences[speaker_id] = {
            'voice_type': voice_type,
            'pitch': pitch,
            'speed': speed,
            'energy': energy
        }
        self._save_preferences()
        
        # Log what speaker ID is being used
        actual_speaker = self.voice_presets.get(voice_type, voice_type)
        print(f"✓ Set preferences for {speaker_id}: {voice_type} → {actual_speaker}")
    
    def get_available_voices(self) -> List[dict]:
        """Get list of available voice options"""
        if not self.is_multi_speaker:
            return [
                {'id': 'default', 'name': 'Default Voice', 'gender': 'neutral'},
            ]
        
        return [
            {'id': 'male_1', 'name': 'Male Voice 1', 'gender': 'male'},
            {'id': 'male_2', 'name': 'Male Voice 2', 'gender': 'male'},
            {'id': 'male_3', 'name': 'Male Voice 3', 'gender': 'male'},
            {'id': 'female_1', 'name': 'Female Voice 1', 'gender': 'female'},
            {'id': 'female_2', 'name': 'Female Voice 2', 'gender': 'female'},
            {'id': 'female_3', 'name': 'Female Voice 3', 'gender': 'female'},
        ]
    
    def synthesize_to_file(self, text: str, output_path: str, 
                          speaker_id: Optional[str] = None,
                          voice_type: Optional[str] = None) -> bool:
        try:
            prefs = self.user_preferences.get(speaker_id, {})
            selected_voice = voice_type or prefs.get('voice_type', 'female_1')
            
            if not self.is_multi_speaker:
                print("⚠ Using single-speaker model (all voices same)")
                self.tts.tts_to_file(text=text, file_path=output_path)
                return True
            
            if self.model_name == "xtts_v2":
                # XTTS requires reference audio
                print(f"🎤 XTTS synthesis: {selected_voice}")
                # For now, use default voice
                self.tts.tts_to_file(
                    text=text,
                    file_path=output_path,
                    language="en"
                )
            else:
                # VCTK or other multi-speaker
                model_speaker = self.voice_presets.get(selected_voice, 'p225')
                print(f"🎤 Synthesis: {selected_voice} → {model_speaker}")
                
                self.tts.tts_to_file(
                    text=text,
                    file_path=output_path,
                    speaker=model_speaker
                )
            
            # Verify file was created
            if os.path.exists(output_path):
                size = os.path.getsize(output_path)
                print(f"✓ Generated {size} bytes")
                return True
            else:
                print(f"✗ File not created")
                return False
                
        except Exception as e:
            print(f"✗ Synthesis failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def synthesize_to_bytes(self, text: str, speaker_id: Optional[str] = None,
                           voice_type: Optional[str] = None) -> Optional[bytes]:
        """Synthesize text and return audio as bytes"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            success = self.synthesize_to_file(text, tmp_path, speaker_id, voice_type)
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
    
    def get_system_info(self) -> Dict:
        """Get information about the TTS system"""
        info = {
            'model': self.model_name,
            'multi_speaker': self.is_multi_speaker,
            'device': self.device,
        }
        
        if self.is_multi_speaker:
            info['voice_presets'] = self.voice_presets
            info['total_speakers'] = len(self.tts.speakers) if hasattr(self.tts, 'speakers') else 0
        
        return info
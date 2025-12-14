from gtts import gTTS
import subprocess
import tempfile
import os
from typing import Optional
import json

class GTTSService:
    """
    Google TTS with speed manipulation for voice variety
    NOTE: Pitch manipulation removed to prevent chipmunk effect
    """
    
    def __init__(self):
        print("🔊 Initializing gTTS service...")
        
        # Check if ffmpeg is available
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            self.has_ffmpeg = True
            print("✓ ffmpeg available for voice manipulation")
        except:
            self.has_ffmpeg = False
            print("⚠ ffmpeg not found - voices will sound similar")
        
        self.is_multi_speaker = True  # We simulate it
        
        # Voice configurations (speed multiplier ONLY - no pitch to avoid chipmunk effect)
        # Voice variety comes from gTTS's different accents/TLDs and subtle speed changes
        self.voice_configs = {
            'american': {'speed': 1.0, 'lang': 'en', 'tld': 'com'},
            'uk': {'speed': 0.95, 'lang': 'en', 'tld': 'co.uk'},
            'mexican': {'speed': 0.98, 'lang': 'es', 'tld': 'com.mx'},
            'african': {'speed': 1.03, 'lang': 'en', 'tld': 'com.ng'},
            'indian': {'speed': 1.05, 'lang': 'en', 'tld': 'co.in'},
            'irish': {'speed': 1.02, 'lang': 'en', 'tld': 'ie'},
            'french': {'speed': 0.97, 'lang': 'fr', 'tld': 'fr'},
            'italian': {'speed': 0.96, 'lang': 'it', 'tld': 'it'},
            'german': {'speed': 0.98, 'lang': 'de', 'tld': 'de'},
        }
        
        self.user_preferences = {}
        self.preferences_file = "tts_preferences.json"
        self._load_preferences()
        
        print(f"✓ gTTS initialized with {len(self.voice_configs)} voice variants")
    
    def _load_preferences(self):
        if os.path.exists(self.preferences_file):
            try:
                with open(self.preferences_file, 'r') as f:
                    self.user_preferences = json.load(f)
            except Exception as e:
                print(f"Error loading preferences: {e}")
    
    def _save_preferences(self):
        try:
            with open(self.preferences_file, 'w') as f:
                json.dump(self.user_preferences, f, indent=2)
        except Exception as e:
            print(f"Error saving preferences: {e}")
    
    def set_user_preferences(self, speaker_id: str, voice_type: str = 'american',
                           pitch: float = 1.0, speed: float = 1.0, energy: float = 1.0):
        self.user_preferences[speaker_id] = {
            'voice_type': voice_type,
            'pitch': pitch,  # Kept for API compatibility but ignored
            'speed': speed,
            'energy': energy
        }
        self._save_preferences()
    
    def synthesize_to_file(self, text: str, output_path: str, 
                          speaker_id: Optional[str] = None,
                          voice_type: Optional[str] = None) -> bool:
        try:
            prefs = self.user_preferences.get(speaker_id, {})
            selected_voice = voice_type or prefs.get('voice_type', 'american')
            
            # Map old voice types to new accent-based ones
            voice_mapping = {
                'male_1': 'american',
                'male_2': 'uk', 
                'male_3': 'german',
                'female_1': 'american',
                'female_2': 'uk',
                'female_3': 'irish'
            }
            selected_voice = voice_mapping.get(selected_voice, selected_voice)
            
            config = self.voice_configs.get(selected_voice, self.voice_configs['american'])
            
            print(f"🎤 gTTS synthesis: {selected_voice} (speed={config['speed']})")
            
            # Generate with gTTS
            tts = gTTS(text=text, lang=config['lang'], tld=config['tld'], slow=False)
            
            # Check if we need speed manipulation
            if not self.has_ffmpeg or abs(config['speed'] - 1.0) < 0.01:
                # Direct save without manipulation if speed is ~1.0 or no ffmpeg
                tts.save(output_path)
                return True
            
            # Save to temp MP3
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
                tmp_mp3 = tmp.name
                tts.save(tmp_mp3)
            
            try:
                # Apply ONLY speed with ffmpeg (NO pitch manipulation)
                # Clamp speed to safe range for atempo (0.5 to 2.0)
                safe_speed = max(0.5, min(2.0, config['speed']))
                
                cmd = [
                    'ffmpeg', '-i', tmp_mp3,
                    '-af', f'atempo={safe_speed}',
                    '-y', output_path
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    print(f"ffmpeg error: {result.stderr}")
                    # Fallback: save without manipulation
                    tts.save(output_path)
                
                return os.path.exists(output_path)
                
            finally:
                if os.path.exists(tmp_mp3):
                    os.unlink(tmp_mp3)
            
        except Exception as e:
            print(f"✗ Synthesis failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def synthesize_to_bytes(self, text: str, speaker_id: Optional[str] = None,
                           voice_type: Optional[str] = None) -> Optional[bytes]:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            success = self.synthesize_to_file(text, tmp_path, speaker_id, voice_type)
            if success:
                with open(tmp_path, 'rb') as f:
                    return f.read()
            return None
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def get_available_voices(self):
        return [
            {'id': 'american', 'name': 'American Accent (US)', 'gender': 'female'},
            {'id': 'african', 'name': 'African Accent (NG)', 'gender': 'female'},
            {'id': 'uk', 'name': 'English Accent (UK)', 'gender': 'female'},
            {'id': 'french', 'name': 'French Accent (FR)', 'gender': 'female'},
            {'id': 'german', 'name': 'German Accent (DE)', 'gender': 'female'},
            {'id': 'indian', 'name': 'Indian Accent (IN)', 'gender': 'female'},
            {'id': 'irish', 'name': 'Irish Accent (IE)', 'gender': 'female'},
            {'id': 'italian', 'name': 'Italian Accent (IT)', 'gender': 'male'},
            {'id': 'mexican', 'name': 'Mexican Accent (MX)', 'gender': 'female'},
        ]
    
    def get_user_preferences(self, speaker_id: str):
        return self.user_preferences.get(speaker_id)
    
    def get_system_info(self):
        return {
            'model': 'gTTS',
            'multi_speaker': True,
            'device': 'cloud',
            'has_ffmpeg': self.has_ffmpeg,
            'voice_configs': self.voice_configs
        }

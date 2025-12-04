from gtts import gTTS
import subprocess
import tempfile
import os
from typing import Optional, List, Dict
import json

class GTTSService:
    """
    Google TTS with pitch/speed manipulation for voice variety
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
        
        # Voice configurations (pitch in semitones, speed multiplier)
        self.voice_configs = {
            'american': {'pitch': 3, 'speed': 0.95, 'lang': 'en', 'tld': 'com'},
            'uk': {'pitch': -5, 'speed': 0.90, 'lang': 'en', 'tld': 'co.uk'},
            'mexican': {'pitch': -4, 'speed': 0.92, 'lang': 'es', 'tld': 'com.mx'},
            'african': {'pitch': 3, 'speed': 1.05, 'lang': 'en', 'tld': 'com.ng'},
            'indian': {'pitch': 4, 'speed': 1.08, 'lang': 'en', 'tld': 'co.in'},
            'irish': {'pitch': 5, 'speed': 1.10, 'lang': 'en', 'tld': 'ie'},
            'french': {'pitch': 5, 'speed': 1.10, 'lang': 'fr', 'tld': 'fr'},
            'italian': {'pitch': -5, 'speed': 0.90, 'lang': 'it', 'tld': 'it'},
            'german': {'pitch': 5, 'speed': 1.10, 'lang': 'de', 'tld': 'de'},
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
            'pitch': pitch,
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
            config = self.voice_configs.get(selected_voice, self.voice_configs['american'])
            
            print(f"🎤 gTTS synthesis: {selected_voice} (pitch={config['pitch']}, speed={config['speed']})")
            
            # Generate with gTTS
            tts = gTTS(text=text, lang=config['lang'], tld=config['tld'], slow=False)
            
            if not self.has_ffmpeg:
                # Direct save without manipulation
                tts.save(output_path)
                return True
            
            # Save to temp MP3
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
                tmp_mp3 = tmp.name
                tts.save(tmp_mp3)
            
            try:
                # Apply pitch and speed with ffmpeg
                pitch_cents = config['pitch'] * 100  # Convert semitones to cents
                
                cmd = [
                    'ffmpeg', '-i', tmp_mp3,
                    '-af', f'asetrate=44100*2^({pitch_cents}/1200),atempo={config["speed"]},aresample=44100',
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
    
    def get_available_voices(self) -> Dict:
        return [
            {'id': 'american', 'name': 'American Accent(US)', 'gender': 'female'},
            {'id': 'african', 'name': 'African Accent(NG)', 'gender': 'female'},
            {'id': 'uk', 'name': 'English Accent(UK)', 'gender': 'female'},
            {'id': 'french', 'name': 'French Accent(FR)', 'gender': 'female'},
            {'id': 'german', 'name': 'German Accent(DE)', 'gender': 'female'},
            {'id': 'indian', 'name': 'Indian Accent(IN)', 'gender': 'female'},
            {'id': 'irish', 'name': 'Irish Accent(IE)', 'gender': 'female'},
            {'id': 'italian', 'name': 'Italian Accent(IT)', 'gender': 'male'},
            {'id': 'mexican', 'name': 'Mexican Accent(MX)', 'gender': 'female'},
        ]
    
    def get_user_preferences(self, speaker_id: str) -> Optional[dict]:
        return self.user_preferences.get(speaker_id)
    
    def get_system_info(self) -> Dict:
        info = {
            'model': 'gTTS',
            'multi_speaker': True,
            'device': 'cloud',
            'has_ffmpeg': self.has_ffmpeg,
            'voice_configs': self.voice_configs,
            'total_speakers': len(self.voice_configs),
        }
        return info
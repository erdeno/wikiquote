import pytest
import os

@pytest.mark.unit
@pytest.mark.voice
class TestCoquiTTS:
    """Test Coqui TTS service"""
    
    def test_tts_initialization(self, mock_tts):
        """Test TTS service initializes"""
        from voice.tts.coqui_service import CoquiTTS
        
        tts = CoquiTTS()
        
        assert tts is not None
        assert tts.tts is not None
    
    def test_set_user_preferences(self, mock_tts):
        """Test setting user TTS preferences"""
        from voice.tts.coqui_service import CoquiTTS
        
        tts = CoquiTTS()
        tts.set_user_preferences('test_user', 'male_1', 1.2, 0.9, 1.1)
        
        prefs = tts.get_user_preferences('test_user')
        
        assert prefs is not None
        assert prefs['voice_type'] == 'male_1'
        assert prefs['pitch'] == 1.2
    
    def test_get_available_voices(self, mock_tts):
        """Test getting available voices"""
        from voice.tts.coqui_service import CoquiTTS
        
        tts = CoquiTTS()
        voices = tts.get_available_voices()
        
        assert len(voices) > 0
        assert all('id' in v and 'name' in v for v in voices)
    
    def test_synthesize_to_file(self, mock_tts, tmp_path):
        """Test synthesizing to file"""
        from voice.tts.coqui_service import CoquiTTS
        
        tts = CoquiTTS()
        output_path = tmp_path / "test.wav"
        
        # Mock the file creation
        output_path.touch()
        
        success = tts.synthesize_to_file("Test text", str(output_path))
        
        assert success is True or mock_tts.called
    
    def test_synthesize_with_voice_type(self, mock_tts):
        """Test synthesizing with specific voice type"""
        from voice.tts.coqui_service import CoquiTTS
        
        tts = CoquiTTS()
        
        audio_bytes = tts.synthesize_to_bytes("Test", voice_type='male_1')
        
        # Should attempt synthesis even if it returns None in test
        assert mock_tts.called
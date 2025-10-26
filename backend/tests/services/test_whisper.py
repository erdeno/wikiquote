import pytest
import numpy as np
import tempfile
import soundfile as sf

@pytest.mark.unit
@pytest.mark.voice
class TestWhisperASR:
    """Test Whisper ASR service"""
    
    def test_whisper_initialization(self, mock_whisper):
        """Test Whisper service initializes correctly"""
        from voice.asr.whisper_service import WhisperASR
        
        asr = WhisperASR(model_size='base')
        
        assert asr is not None
        assert asr.model is not None
        mock_whisper.assert_called_once()
    
    def test_transcribe_file(self, mock_whisper):
        """Test transcribing audio file"""
        from voice.asr.whisper_service import WhisperASR
        
        asr = WhisperASR()
        
        # Create temp audio file
        sample_rate = 16000
        duration = 1.0
        samples = np.zeros(int(sample_rate * duration))
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            sf.write(tmp.name, samples, sample_rate)
            
            result = asr.transcribe(tmp.name)
            
            assert 'text' in result
            assert 'language' in result
            assert result['text'] == 'test transcription'
    
    def test_transcribe_bytes(self, mock_whisper, sample_audio_bytes):
        """Test transcribing audio from bytes"""
        from voice.asr.whisper_service import WhisperASR
        
        asr = WhisperASR()
        result = asr.transcribe_bytes(sample_audio_bytes)
        
        assert 'text' in result
        assert isinstance(result['text'], str)
    
    def test_transcribe_with_language(self, mock_whisper):
        """Test transcription with specified language"""
        from voice.asr.whisper_service import WhisperASR
        
        asr = WhisperASR()
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            sample_rate = 16000
            samples = np.zeros(int(sample_rate * 1.0))
            sf.write(tmp.name, samples, sample_rate)
            
            result = asr.transcribe(tmp.name, language='en')
            
            assert result['language'] == 'en'
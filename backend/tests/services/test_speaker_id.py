import pytest
import numpy as np
import os
import json

@pytest.mark.unit
@pytest.mark.voice
class TestSpeakerIdentifier:
    """Test Speaker Identification service"""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Clean up speaker embeddings before and after each test"""
        embedding_file = "speaker_embeddings.json"
        
        # Backup existing file
        backup_file = None
        if os.path.exists(embedding_file):
            backup_file = f"{embedding_file}.backup"
            if os.path.exists(backup_file):
                os.remove(backup_file)
            os.rename(embedding_file, backup_file)
        
        # Run test
        yield
        
        # Cleanup test file
        if os.path.exists(embedding_file):
            os.remove(embedding_file)
        
        # Restore backup
        if backup_file and os.path.exists(backup_file):
            os.rename(backup_file, embedding_file)
    
    def test_speaker_id_initialization(self, mock_speechbrain):
        """Test speaker ID service initializes"""
        from voice.speaker_id.ecapa_service import SpeakerIdentifier
        
        speaker_id = SpeakerIdentifier()
        
        assert speaker_id is not None
        assert speaker_id.classifier is not None
        # Check embeddings are empty after fresh init
        assert len(speaker_id.speaker_embeddings) == 0
    
    def test_extract_embedding(self, mock_speechbrain, sample_audio_bytes):
        """Test extracting speaker embedding"""
        from voice.speaker_id.ecapa_service import SpeakerIdentifier
        import tempfile
        
        speaker_id = SpeakerIdentifier()
        
        # Write bytes to temp file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            tmp.write(sample_audio_bytes)
            tmp.flush()
            
            embedding = speaker_id.extract_embedding(tmp.name)
            
            assert isinstance(embedding, np.ndarray)
            assert len(embedding) > 0
            
            os.unlink(tmp.name)
    
    def test_register_speaker(self, mock_speechbrain, sample_audio_bytes):
        """Test registering a speaker"""
        from voice.speaker_id.ecapa_service import SpeakerIdentifier
        
        speaker_id = SpeakerIdentifier()
        
        # Should start with 0 speakers
        assert len(speaker_id.speaker_embeddings) == 0
        
        success = speaker_id.register_speaker('test_user', sample_audio_bytes)
        
        assert success is True
        assert 'test_user' in speaker_id.speaker_embeddings
        assert len(speaker_id.speaker_embeddings) == 1
    
    def test_identify_speaker(self, mock_speechbrain, sample_audio_bytes):
        """Test identifying a registered speaker"""
        from voice.speaker_id.ecapa_service import SpeakerIdentifier
        
        speaker_id = SpeakerIdentifier()
        
        # Register speaker
        speaker_id.register_speaker('test_user', sample_audio_bytes)
        
        # Identify same speaker
        identified = speaker_id.identify_speaker(sample_audio_bytes, threshold=1.0)
        
        assert identified == 'test_user'
    
    def test_identify_unknown_speaker(self, mock_speechbrain, sample_audio_bytes):
        """Test identifying unknown speaker returns None"""
        from voice.speaker_id.ecapa_service import SpeakerIdentifier
        
        speaker_id = SpeakerIdentifier()
        
        # Try to identify without registering
        identified = speaker_id.identify_speaker(sample_audio_bytes)
        
        assert identified is None
    
    def test_get_registered_speakers(self, mock_speechbrain, sample_audio_bytes):
        """Test getting list of registered speakers"""
        from voice.speaker_id.ecapa_service import SpeakerIdentifier
        
        speaker_id = SpeakerIdentifier()
        
        # Should start empty
        speakers = speaker_id.get_registered_speakers()
        assert len(speakers) == 0
        
        # Register 2 speakers
        speaker_id.register_speaker('user1', sample_audio_bytes)
        speaker_id.register_speaker('user2', sample_audio_bytes)
        
        speakers = speaker_id.get_registered_speakers()
        
        assert len(speakers) == 2
        assert 'user1' in speakers
        assert 'user2' in speakers
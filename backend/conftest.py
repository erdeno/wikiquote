import pytest
import os
import sys
import django
from django.conf import settings

# Configure Django settings before any imports
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

# Set SECRET_KEY for tests
os.environ.setdefault('SECRET_KEY', 'test-secret-key-for-testing-only-12345')

# Add project root to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# Add services to path
services_path = os.path.join(BASE_DIR, '..', 'services')
if services_path not in sys.path:
    sys.path.insert(0, services_path)

# Setup Django
django.setup()

@pytest.fixture
def api_client():
    """Provide Django REST framework API client"""
    from rest_framework.test import APIClient
    return APIClient()

@pytest.fixture
def authenticated_client(api_client, django_user_model):
    """Provide authenticated API client"""
    from rest_framework.authtoken.models import Token
    
    user = django_user_model.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    token = Token.objects.create(user=user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    api_client.user = user
    return api_client

@pytest.fixture
def sample_audio_bytes():
    """Provide sample audio data for testing"""
    import numpy as np
    import soundfile as sf
    import tempfile
    
    # Generate 1 second of silence at 16kHz
    sample_rate = 16000
    duration = 1.0
    samples = np.zeros(int(sample_rate * duration))
    
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
        sf.write(tmp.name, samples, sample_rate)
        tmp.seek(0)
        audio_bytes = open(tmp.name, 'rb').read()
        os.unlink(tmp.name)
    
    return audio_bytes

@pytest.fixture
def mock_whisper(mocker):
    """Mock Whisper ASR service"""
    mock = mocker.patch('voice.asr.whisper_service.whisper.load_model')
    mock_model = mocker.MagicMock()
    mock_model.transcribe.return_value = {
        'text': 'test transcription',
        'language': 'en',
        'segments': []
    }
    mock.return_value = mock_model
    return mock

@pytest.fixture
def mock_speechbrain(mocker):
    """Mock SpeechBrain speaker recognition"""
    mock = mocker.patch('voice.speaker_id.ecapa_service.EncoderClassifier.from_hparams')
    mock_classifier = mocker.MagicMock()
    
    import numpy as np
    mock_embedding = np.random.rand(192)
    mock_classifier.encode_batch.return_value = mocker.MagicMock(
        squeeze=lambda: mocker.MagicMock(
            cpu=lambda: mocker.MagicMock(
                numpy=lambda: mock_embedding
            )
        )
    )
    
    mock.return_value = mock_classifier
    return mock

@pytest.fixture
def mock_tts(mocker):
    """Mock gTTS service"""
    # Mock gTTS class
    mock_gtts = mocker.patch('services.voice.tts.gtts_service.gTTS')
    mock_gtts_instance = mocker.MagicMock()
    mock_gtts_instance.save.return_value = None
    mock_gtts.return_value = mock_gtts_instance

    # Mock subprocess (ffmpeg)
    mocker.patch('services.voice.tts.gtts_service.subprocess.run')

    return mock_gtts

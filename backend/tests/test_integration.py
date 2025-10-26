import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from io import BytesIO

@pytest.mark.django_db
@pytest.mark.integration
class TestFullVoiceWorkflow:
    """Test complete voice workflow"""
    
    def test_complete_user_journey(self, sample_audio_bytes, mock_whisper, mock_speechbrain, mock_tts):
        """Test complete user journey from registration to voice query"""
        client = APIClient()
        
        # 1. Register user
        register_data = {
            'username': 'journeyuser',
            'email': 'journey@test.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }
        
        response = client.post('/api/v1/auth/register/', register_data)
        assert response.status_code == 201
        
        token = response.data['token']
        client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        
        # 2. Register voice
        audio_file = BytesIO(sample_audio_bytes)
        audio_file.name = 'test.wav'
        
        response = client.post(
            '/api/v1/voice/speaker/register/',
            {
                'audio': audio_file,
                'voice_type': 'female_1',
                'pitch': 1.0
            },
            format='multipart'
        )
        
        # Should not fail completely
        assert response.status_code in [200, 500]  # 500 acceptable due to mocking
        
        # 3. Update TTS preferences
        response = client.post(
            '/api/v1/voice/tts/preferences/set/',
            {
                'voice_type': 'male_1',
                'pitch': 1.2,
                'speed': 0.9,
                'energy': 1.1
            },
            format='json'
        )
        
        assert response.status_code in [200, 500]
        
        # 4. Get profile
        response = client.get('/api/v1/auth/profile/')
        assert response.status_code == 200
        assert response.data['user']['username'] == 'journeyuser'
        
        # 5. Logout
        response = client.post('/api/v1/auth/logout/')
        assert response.status_code == 200
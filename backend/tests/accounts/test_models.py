import pytest
from django.contrib.auth.models import User
from backend.accounts.models import UserProfile

@pytest.mark.django_db
class TestUserProfile:
    """Test UserProfile model"""
    
    def test_profile_created_on_user_creation(self):
        """Test that profile is automatically created when user is created"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        assert hasattr(user, 'profile')
        assert isinstance(user.profile, UserProfile)
        assert user.profile.user == user
    
    def test_profile_default_values(self):
        """Test profile default values"""
        user = User.objects.create_user(username='testuser', password='test')
        profile = user.profile
        
        assert profile.voice_registered is False
        assert profile.tts_voice_type == 'female_1'
        assert profile.tts_pitch == 1.0
        assert profile.tts_speed == 1.0
        assert profile.tts_energy == 1.0
        assert profile.queries_count == 0
        assert profile.last_query is None
    
    def test_profile_str_method(self):
        """Test profile string representation"""
        user = User.objects.create_user(username='testuser', password='test')
        assert str(user.profile) == "testuser's profile"
    
    def test_voice_type_choices(self):
        """Test voice type choices"""
        user = User.objects.create_user(username='testuser', password='test')
        profile = user.profile
        
        valid_choices = ['male_1', 'male_2', 'male_3', 'female_1', 'female_2', 'female_3']
        
        for choice in valid_choices:
            profile.tts_voice_type = choice
            profile.save()
            profile.refresh_from_db()
            assert profile.tts_voice_type == choice
    
    def test_update_profile_preferences(self):
        """Test updating TTS preferences"""
        user = User.objects.create_user(username='testuser', password='test')
        profile = user.profile
        
        profile.tts_voice_type = 'male_2'
        profile.tts_pitch = 1.2
        profile.tts_speed = 0.9
        profile.tts_energy = 1.1
        profile.voice_registered = True
        profile.save()
        
        profile.refresh_from_db()
        assert profile.tts_voice_type == 'male_2'
        assert profile.tts_pitch == 1.2
        assert profile.tts_speed == 0.9
        assert profile.tts_energy == 1.1
        assert profile.voice_registered is True
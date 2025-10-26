import pytest
from django.contrib.auth.models import User
from rest_framework import status

@pytest.mark.django_db
class TestAuthenticationViews:
    """Test authentication endpoints"""
    
    def test_register_success(self, api_client):
        """Test successful user registration"""
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'securepass123',
            'password_confirm': 'securepass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = api_client.post('/api/v1/auth/register/', data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['success'] is True
        assert 'token' in response.data
        assert 'user' in response.data
        
        # Verify user was created
        user = User.objects.get(username='newuser')
        assert user.email == 'new@example.com'
        assert user.first_name == 'New'
    
    def test_register_password_mismatch(self, api_client):
        """Test registration with mismatched passwords"""
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'password123',
            'password_confirm': 'different123'
        }
        
        response = api_client.post('/api/v1/auth/register/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_register_duplicate_username(self, api_client):
        """Test registration with existing username"""
        User.objects.create_user(username='existing', password='pass')
        
        data = {
            'username': 'existing',
            'email': 'new@example.com',
            'password': 'password123',
            'password_confirm': 'password123'
        }
        
        response = api_client.post('/api/v1/auth/register/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_login_success(self, api_client):
        """Test successful login"""
        User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = api_client.post('/api/v1/auth/login/', data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert 'token' in response.data
        assert 'user' in response.data
    
    def test_login_invalid_credentials(self, api_client):
        """Test login with invalid credentials"""
        data = {
            'username': 'nonexistent',
            'password': 'wrongpass'
        }
        
        response = api_client.post('/api/v1/auth/login/', data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_logout_success(self, authenticated_client):
        """Test successful logout"""
        response = authenticated_client.post('/api/v1/auth/logout/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
    
    def test_get_profile_authenticated(self, authenticated_client):
        """Test getting profile when authenticated"""
        response = authenticated_client.get('/api/v1/auth/profile/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert 'user' in response.data
    
    def test_get_profile_unauthenticated(self, api_client):
        """Test getting profile when not authenticated"""
        response = api_client.get('/api/v1/auth/profile/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_update_profile(self, authenticated_client):
        """Test updating profile"""
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'bio': 'Test bio',
            'tts_pitch': 1.2,
            'tts_speed': 0.9
        }
        
        response = authenticated_client.put('/api/v1/auth/profile/update/', data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        
        # Verify update
        authenticated_client.user.refresh_from_db()
        assert authenticated_client.user.first_name == 'Updated'
        assert authenticated_client.user.profile.tts_pitch == 1.2
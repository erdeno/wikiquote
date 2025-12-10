from django.contrib.auth.backends import BaseBackend
from .neo_models import NeoUser, NeoAuthToken
from neomodel import db

class NeoModelAuthBackend(BaseBackend):
    """Authentication backend using Neo4j"""
    
    def authenticate(self, request, username=None, password=None):
        try:
            user = NeoUser.nodes.get(username=username)
            if user.check_password(password):
                return self._create_django_user(user)
        except NeoUser.DoesNotExist:
            return None
        return None
    
    def get_user(self, user_id):
        try:
            user = NeoUser.nodes.get(uid=user_id)
            return self._create_django_user(user)
        except NeoUser.DoesNotExist:
            return None
    
    def _create_django_user(self, neo_user):
        """Create a minimal Django user object from Neo4j user"""
        from django.contrib.auth.models import AnonymousUser
        
        class NeoBackedUser:
            def __init__(self, neo_user):
                self.id = neo_user.uid
                self.username = neo_user.username
                self.email = neo_user.email
                self.is_active = neo_user.is_active
                self.is_authenticated = True
                self.neo_user = neo_user
            
            def __str__(self):
                return self.username
        
        return NeoBackedUser(neo_user)

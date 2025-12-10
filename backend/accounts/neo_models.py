from neomodel import (
    StructuredNode, StringProperty, EmailProperty, 
    DateTimeProperty, IntegerProperty, FloatProperty,
    RelationshipTo, UniqueIdProperty
)
from django.contrib.auth.hashers import make_password, check_password
from datetime import datetime

class NeoUser(StructuredNode):
    """Neo4j User model"""
    uid = UniqueIdProperty()
    username = StringProperty(unique_index=True, required=True)
    email = EmailProperty(unique_index=True)
    password = StringProperty(required=True)  # Hashed
    first_name = StringProperty(default='')
    last_name = StringProperty(default='')
    is_active = BooleanProperty(default=True)
    date_joined = DateTimeProperty(default_now=True)
    
    # User Profile fields (merged)
    tts_voice_type = StringProperty(default='american')
    tts_pitch = FloatProperty(default=1.0)
    tts_speed = FloatProperty(default=1.0)
    tts_energy = FloatProperty(default=1.0)
    bio = StringProperty(default='')
    queries_count = IntegerProperty(default=0)
    last_query = DateTimeProperty()
    
    # Relationships
    saved_quotes = RelationshipTo('Quote', 'SAVED')
    
    def set_password(self, raw_password):
        """Hash and set password"""
        self.password = make_password(raw_password)
        self.save()
    
    def check_password(self, raw_password):
        """Check password"""
        return check_password(raw_password, self.password)
    
    @classmethod
    def create_user(cls, username, email, password, **extra_fields):
        """Create new user"""
        user = cls(
            username=username,
            email=email,
            password=make_password(password),
            **extra_fields
        )
        user.save()
        return user


class NeoAuthToken(StructuredNode):
    """Neo4j Token model"""
    key = StringProperty(unique_index=True, required=True)
    user_id = StringProperty(required=True)  # Link to NeoUser uid
    created = DateTimeProperty(default_now=True)

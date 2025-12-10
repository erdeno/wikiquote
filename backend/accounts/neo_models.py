from neomodel import (
    StructuredNode, StringProperty, EmailProperty, 
    DateTimeProperty, IntegerProperty, FloatProperty,
    RelationshipTo, UniqueIdProperty, BooleanProperty
)
from django.contrib.auth.hashers import make_password, check_password
from datetime import datetime

class NeoUser(StructuredNode):
    """Neo4j User model"""
    uid = UniqueIdProperty()
    username = StringProperty(unique_index=True, required=True)
    email = EmailProperty(unique_index=True)
    password = StringProperty(required=True)
    first_name = StringProperty(default='')
    last_name = StringProperty(default='')
    is_active = BooleanProperty(default=True)  # Fixed: Added BooleanProperty
    date_joined = DateTimeProperty(default_now=True)
    
    # Profile fields
    tts_voice_type = StringProperty(default='american')
    tts_pitch = FloatProperty(default=1.0)
    tts_speed = FloatProperty(default=1.0)
    tts_energy = FloatProperty(default=1.0)
    bio = StringProperty(default='')
    queries_count = IntegerProperty(default=0)
    last_query = DateTimeProperty()
    
    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save()
    
    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    
    @classmethod
    def create_user(cls, username, email, password, **extra_fields):
        user = cls(
            username=username,
            email=email,
            password=make_password(password),
            **extra_fields
        )
        user.save()
        return user


class NeoAuthToken(StructuredNode):
    """Auth token"""
    key = StringProperty(unique_index=True, required=True)
    user_id = StringProperty(required=True)
    created = DateTimeProperty(default_now=True)
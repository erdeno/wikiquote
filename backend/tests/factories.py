import factory
from factory.django import DjangoModelFactory
from django.contrib.auth.models import User
from accounts.models import UserProfile

class UserFactory(DjangoModelFactory):
    """Factory for creating test users"""
    
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    
    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        if not create:
            return
        
        if extracted:
            self.set_password(extracted)
        else:
            self.set_password('defaultpass123')

class UserProfileFactory(DjangoModelFactory):
    """Factory for creating test user profiles"""
    
    class Meta:
        model = UserProfile
    
    user = factory.SubFactory(UserFactory)
    voice_registered = False
    tts_voice_type = 'female_1'
    tts_pitch = 1.0
    tts_speed = 1.0
    tts_energy = 1.0
    queries_count = 0
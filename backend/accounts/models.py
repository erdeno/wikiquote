from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    """
    Extended user profile with voice preferences
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Voice settings
    voice_registered = models.BooleanField(default=False)
    voice_embedding_file = models.CharField(max_length=255, blank=True, null=True)
    
    # TTS preferences
    tts_pitch = models.FloatField(default=1.0)
    tts_speed = models.FloatField(default=1.0)
    tts_energy = models.FloatField(default=1.0)
    
    # Profile info
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    
    # Statistics
    queries_count = models.IntegerField(default=0)
    last_query = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s profile"
    
    class Meta:
        db_table = 'user_profiles'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create profile automatically when user is created"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save profile when user is saved"""
    instance.profile.save()
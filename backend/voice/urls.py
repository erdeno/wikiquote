from django.urls import path
from . import views

app_name = 'voice'

urlpatterns = [
    # ASR endpoint
    path('transcribe/', views.transcribe_audio, name='transcribe'),
    
    path('speaker/list/', views.list_speakers, name='list_speakers'),    
    # TTS endpoints
    path('synthesize/', views.synthesize_speech, name='synthesize'),
    path('voices/', views.get_available_voices, name='available_voices'),
    path('tts/info/', views.get_tts_info, name='tts_info'),
    path('tts/preferences/set/', views.set_tts_preferences, name='set_tts_preferences'),
    path('tts/preferences/get/', views.get_tts_preferences, name='get_tts_preferences'),
    
    # Full voice query pipeline
    path('query/', views.voice_query, name='voice_query'),
]

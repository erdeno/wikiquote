from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from django.conf import settings
from django.utils import timezone
import os
import sys
import base64


# Import services
from services.voice.asr.whisper_service import WhisperASR
from services.voice.speaker_id.ecapa_service import SpeakerIdentifier
from services.voice.tts.coqui_service import CoquiTTS
from .chatbot import QuoteChatbot

# Initialize services (singleton pattern)
asr_service = None
speaker_service = None
tts_service = None

def get_asr_service():
    global asr_service
    if asr_service is None:
        asr_service = WhisperASR(model_size="base")
    return asr_service

def get_speaker_service():
    global speaker_service
    if speaker_service is None:
        speaker_service = SpeakerIdentifier()
    return speaker_service

def get_tts_service():
    global tts_service
    if tts_service is None:
        tts_service = CoquiTTS()
    return tts_service


@api_view(['POST'])
@permission_classes([AllowAny])
def transcribe_audio(request):
    """ASR endpoint: transcribe audio to text"""
    if 'audio' not in request.FILES:
        return Response(
            {'error': 'No audio file provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    audio_file = request.FILES['audio']
    language = request.data.get('language', None)
    
    try:
        asr = get_asr_service()
        audio_bytes = audio_file.read()
        result = asr.transcribe_bytes(audio_bytes, language)
        
        return Response({
            'success': True,
            'transcription': result['text'],
            'language': result['language']
        })
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_speaker(request):
    """Register authenticated user's voice"""
    if 'audio' not in request.FILES:
        return Response(
            {'error': 'Missing audio file'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    audio_file = request.FILES['audio']
    user = request.user
    speaker_id = user.username
    
    # Get TTS preferences
    pitch = float(request.data.get('pitch', 1.0))
    speed = float(request.data.get('speed', 1.0))
    energy = float(request.data.get('energy', 1.0))
    
    try:
        speaker_svc = get_speaker_service()
        audio_bytes = audio_file.read()
        
        success = speaker_svc.register_speaker(speaker_id, audio_bytes)
        
        if success:
            # Update user profile
            profile = user.profile
            profile.voice_registered = True
            profile.tts_pitch = pitch
            profile.tts_speed = speed
            profile.tts_energy = energy
            profile.save()
            
            # Set TTS preferences
            tts = get_tts_service()
            tts.set_user_preferences(speaker_id, pitch, speed, energy)
            
            return Response({
                'success': True,
                'message': f'Voice registered successfully for {user.username}'
            })
        else:
            return Response(
                {'error': 'Registration failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def identify_speaker(request):
    """Identify speaker from audio"""
    if 'audio' not in request.FILES:
        return Response(
            {'error': 'No audio file provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    audio_file = request.FILES['audio']
    threshold = float(request.data.get('threshold', 0.25))
    
    try:
        speaker_svc = get_speaker_service()
        audio_bytes = audio_file.read()
        speaker_id = speaker_svc.identify_speaker(audio_bytes, threshold)
        
        return Response({
            'success': True,
            'speaker_id': speaker_id,
            'identified': speaker_id is not None
        })
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def synthesize_speech(request):
    """TTS endpoint: convert text to speech"""
    text = request.data.get('text')
    speaker_id = request.data.get('speaker_id')
    
    if not text:
        return Response(
            {'error': 'No text provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        tts = get_tts_service()
        audio_bytes = tts.synthesize_to_bytes(text, speaker_id=speaker_id)
        
        if audio_bytes:
            response = HttpResponse(audio_bytes, content_type='audio/wav')
            response['Content-Disposition'] = 'attachment; filename="speech.wav"'
            return response
        else:
            return Response(
                {'error': 'TTS synthesis failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def list_speakers(request):
    """List all registered speakers"""
    try:
        speaker_svc = get_speaker_service()
        speakers = speaker_svc.get_registered_speakers()
        
        return Response({
            'success': True,
            'speakers': speakers,
            'count': len(speakers)
        })
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def voice_query(request):
    """
    Complete voice pipeline:
    ASR → Speaker ID → Quote Search → Chatbot → Personalized TTS
    """
    if 'audio' not in request.FILES:
        return Response(
            {'error': 'No audio file provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    audio_file = request.FILES['audio']
    user = request.user
    
    try:
        audio_bytes = audio_file.read()
        
        # Step 1: Transcribe (ASR)
        asr = get_asr_service()
        transcription_result = asr.transcribe_bytes(audio_bytes)
        user_query = transcription_result['text']
        
        # Step 2: Identify speaker
        speaker_svc = get_speaker_service()
        speaker_id = speaker_svc.identify_speaker(audio_bytes, threshold=0.25)
        
        # Step 3: Process query with chatbot
        chatbot = QuoteChatbot()
        chat_result = chatbot.process_query(user_query)
        response_text = chat_result['response']
        
        # Step 4: Synthesize with personalized TTS
        tts = get_tts_service()
        response_audio = tts.synthesize_to_bytes(response_text, speaker_id=user.username)
        
        # Update user statistics
        profile = user.profile
        profile.queries_count += 1
        profile.last_query = timezone.now()
        profile.save()
        
        # Encode audio
        audio_base64 = base64.b64encode(response_audio).decode('utf-8') if response_audio else None
        
        return Response({
            'success': True,
            'transcription': user_query,
            'response_text': response_text,
            'response_audio': audio_base64,
            'identified_speaker': speaker_id,
            'matches_user': speaker_id == user.username if speaker_id else False,
            'quote_found': chat_result['quote_found'],
            'quote_data': chat_result['quote_data']
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_tts_preferences(request):
    """Set TTS preferences for authenticated user"""
    pitch = float(request.data.get('pitch', 1.0))
    speed = float(request.data.get('speed', 1.0))
    energy = float(request.data.get('energy', 1.0))
    
    user = request.user
    
    try:
        # Update profile
        profile = user.profile
        profile.tts_pitch = pitch
        profile.tts_speed = speed
        profile.tts_energy = energy
        profile.save()
        
        # Update TTS service
        tts = get_tts_service()
        tts.set_user_preferences(user.username, pitch, speed, energy)
        
        return Response({
            'success': True,
            'message': f'TTS preferences updated for {user.username}',
            'preferences': {
                'pitch': pitch,
                'speed': speed,
                'energy': energy
            }
        })
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_tts_preferences(request):
    """Get TTS preferences for authenticated user"""
    user = request.user
    profile = user.profile
    
    return Response({
        'success': True,
        'preferences': {
            'pitch': profile.tts_pitch,
            'speed': profile.tts_speed,
            'energy': profile.tts_energy
        }
    })
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from django.conf import settings
import os
import sys
import base64


# Import NeMo services
from services.voice.asr.whisper_service import WhisperASR
from services.voice.speaker_id.titanet_nemo_service import NeMoSpeakerRecognition
from services.voice.tts.nemo_tts_service import NeMoTTS
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
        speaker_service = NeMoSpeakerRecognition(model_name="titanet_large")
    return speaker_service

def get_tts_service():
    global tts_service
    if tts_service is None:
        tts_service = NeMoTTS(model_type="fastpitch_hifigan")
    return tts_service


@api_view(['POST'])
def transcribe_audio(request):
    """
    ASR endpoint: transcribe audio to text
    """
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
def register_speaker(request):
    """
    Register a new speaker with NeMo TitaNet
    """
    if 'audio' not in request.FILES or 'speaker_id' not in request.data:
        return Response(
            {'error': 'Missing audio file or speaker_id'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    audio_file = request.FILES['audio']
    speaker_id = request.data['speaker_id']
    
    # Optional: TTS preferences
    pitch = float(request.data.get('pitch', 1.0))
    speed = float(request.data.get('speed', 1.0))
    energy = float(request.data.get('energy', 1.0))
    
    try:
        speaker_svc = get_speaker_service()
        audio_bytes = audio_file.read()
        
        # Register speaker
        result = speaker_svc.register_speaker(speaker_id, audio_bytes)
        
        if result['success']:
            # Set TTS preferences
            tts = get_tts_service()
            tts.set_user_preferences(speaker_id, pitch, speed, energy)
            
            return Response({
                'success': True,
                'message': f'Speaker {speaker_id} registered successfully',
                'embedding_dim': result['embedding_dim']
            })
        else:
            return Response(
                {'error': result.get('error', 'Registration failed')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def identify_speaker(request):
    """
    Identify speaker from audio using NeMo TitaNet
    """
    if 'audio' not in request.FILES:
        return Response(
            {'error': 'No audio file provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    audio_file = request.FILES['audio']
    threshold = float(request.data.get('threshold', 0.7))
    
    try:
        speaker_svc = get_speaker_service()
        audio_bytes = audio_file.read()
        result = speaker_svc.identify_speaker(audio_bytes, threshold)
        
        if result:
            return Response({
                'success': True,
                'speaker_id': result['speaker_id'],
                'confidence': result['confidence'],
                'identified': True
            })
        else:
            return Response({
                'success': True,
                'speaker_id': None,
                'identified': False,
                'message': 'No confident match found'
            })
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def synthesize_speech(request):
    """
    TTS endpoint using NeMo: convert text to speech
    """
    text = request.data.get('text')
    speaker_id = request.data.get('speaker_id')  # Optional
    
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
def list_speakers(request):
    """
    List all registered speakers
    """
    try:
        speaker_svc = get_speaker_service()
        speakers = speaker_svc.get_registered_speakers()
        stats = speaker_svc.get_embedding_stats()
        
        return Response({
            'success': True,
            'speakers': speakers,
            'stats': stats
        })
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def voice_query(request):
    """
    Complete voice pipeline with personalized TTS:
    ASR → Speaker ID → Quote Search → Chatbot → Personalized TTS
    """
    if 'audio' not in request.FILES:
        return Response(
            {'error': 'No audio file provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    audio_file = request.FILES['audio']
    
    try:
        audio_bytes = audio_file.read()
        
        # Step 1: Transcribe audio (ASR)
        asr = get_asr_service()
        transcription_result = asr.transcribe_bytes(audio_bytes)
        user_query = transcription_result['text']
        
        # Step 2: Identify speaker
        speaker_svc = get_speaker_service()
        speaker_result = speaker_svc.identify_speaker(audio_bytes, threshold=0.7)
        speaker_id = speaker_result['speaker_id'] if speaker_result else None
        confidence = speaker_result['confidence'] if speaker_result else 0.0
        
        # Step 3: Process query with chatbot
        chatbot = QuoteChatbot()
        chat_result = chatbot.process_query(user_query)
        response_text = chat_result['response']
        
        # Step 4: Synthesize response with personalized TTS
        tts = get_tts_service()
        response_audio = tts.synthesize_to_bytes(response_text, speaker_id=speaker_id)
        
        # Encode audio as base64
        audio_base64 = base64.b64encode(response_audio).decode('utf-8') if response_audio else None
        
        return Response({
            'success': True,
            'transcription': user_query,
            'response_text': response_text,
            'response_audio': audio_base64,
            'speaker_id': speaker_id,
            'speaker_confidence': confidence,
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
def set_tts_preferences(request):
    """
    Set TTS preferences for a speaker
    """
    speaker_id = request.data.get('speaker_id')
    pitch = float(request.data.get('pitch', 1.0))
    speed = float(request.data.get('speed', 1.0))
    energy = float(request.data.get('energy', 1.0))
    
    if not speaker_id:
        return Response(
            {'error': 'speaker_id required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        tts = get_tts_service()
        tts.set_user_preferences(speaker_id, pitch, speed, energy)
        
        return Response({
            'success': True,
            'message': f'TTS preferences set for {speaker_id}',
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
def get_tts_preferences(request):
    """
    Get TTS preferences for a speaker
    """
    speaker_id = request.query_params.get('speaker_id')
    
    if not speaker_id:
        return Response(
            {'error': 'speaker_id required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        tts = get_tts_service()
        preferences = tts.get_user_preferences(speaker_id)
        
        if preferences:
            return Response({
                'success': True,
                'speaker_id': speaker_id,
                'preferences': preferences
            })
        else:
            return Response({
                'success': False,
                'message': f'No preferences found for {speaker_id}'
            })
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

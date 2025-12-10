from .neo_models import NeoUser, NeoAuthToken
from rest_framework.decorators import api_view
from rest_framework.response import Response
import secrets

@api_view(['POST'])
def register(request):
    """Register using Neo4j"""
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    
    # Check if user exists
    if NeoUser.nodes.filter(username=username).first():
        return Response({
            'success': False,
            'errors': {'username': ['Username already exists']}
        }, status=400)
    
    # Create user
    try:
        user = NeoUser.create_user(
            username=username,
            email=email,
            password=password
        )
        
        # Create token
        token_key = secrets.token_hex(20)
        token = NeoAuthToken(key=token_key, user_id=user.uid)
        token.save()
        
        return Response({
            'success': True,
            'user': {
                'id': user.uid,
                'username': user.username,
                'email': user.email
            },
            'token': token_key
        })
    except Exception as e:
        return Response({
            'success': False,
            'errors': {'detail': str(e)}
        }, status=400)


@api_view(['POST'])
def login(request):
    """Login using Neo4j"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    try:
        user = NeoUser.nodes.get(username=username)
        
        if user.check_password(password):
            # Get or create token
            token = NeoAuthToken.nodes.filter(user_id=user.uid).first()
            if not token:
                token_key = secrets.token_hex(20)
                token = NeoAuthToken(key=token_key, user_id=user.uid)
                token.save()
            
            return Response({
                'success': True,
                'user': {
                    'id': user.uid,
                    'username': user.username,
                    'email': user.email
                },
                'token': token.key
            })
        else:
            return Response({
                'success': False,
                'errors': {'detail': 'Invalid credentials'}
            }, status=401)
            
    except NeoUser.DoesNotExist:
        return Response({
            'success': False,
            'errors': {'detail': 'Invalid credentials'}
        }, status=401)

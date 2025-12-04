from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .neo4j_client import run_read, run_read_one, health_check_details
from .cypher import AUTOCOMPLETE, DETAIL_BY_ID
from .serializers import QueryHistorySerializer, FavoriteQuoteSerializer
from .models import QueryHistory, FavoriteQuote
from services.rag.rag_chatbot import RAGChatbot
from django.conf import settings
from dotenv import load_dotenv
import os

# Load credentials
load_dotenv()
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")


@api_view(['GET'])
@permission_classes([AllowAny])
def healthz(request):
    """Health check endpoint"""
    details = health_check_details()
    return Response(
        {"neo4j_ok": details["ok"], "error": details["error"]},
        status=200
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def search_quotes(request):
    """Search quotes endpoint"""
    q = (request.query_params.get("q") or "").strip()
    try:
        k = int(request.query_params.get("k", 8))
    except ValueError:
        k = 8
    k = max(1, min(k, 20))
    
    if len(q) < 2:
        return Response({"results": [], "query": q, "count": 0}, status=200)

    try:
        rows = run_read(AUTOCOMPLETE, {"q": q, "k": k})
        hits = [{
            "quote_id": r["qid"],
            "text": r["short_text"],
            "short_text": r["short_text"],
            "full_text": r["full_text"],
            "author": r.get("author"),
            "score": r["score"],
        } for r in rows]
        
        # Track query history (only if user is authenticated)
        if request.user and request.user.is_authenticated:
            try:
                QueryHistory.objects.create(
                    user=request.user,
                    query_text=q,
                    results_found=len(hits)
                )
            except Exception as e:
                print(f"Failed to log query: {e}")  # Just log, don't break
        
        return Response({
            "success": True,
            "results": hits,
            "query": q,
            "count": len(hits)
        }, status=200)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({
            "success": False,
            "error": str(e),
            "results": [],
            "query": q
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_query_history(request):
    """Get user's query history"""
    limit = int(request.query_params.get('limit', 20))
    
    history = QueryHistory.objects.filter(user=request.user)[:limit]
    serializer = QueryHistorySerializer(history, many=True)
    
    return Response({
        'success': True,
        'history': serializer.data,
        'total': QueryHistory.objects.filter(user=request.user).count()
    })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_query_history(request):
    """Clear user's query history"""
    deleted = QueryHistory.objects.filter(user=request.user).delete()
    
    return Response({
        'success': True,
        'deleted': deleted[0]
    })


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def favorite_quotes(request):
    """Get or add favorite quotes"""
    
    if request.method == 'GET':
        favorites = FavoriteQuote.objects.filter(user=request.user)
        serializer = FavoriteQuoteSerializer(favorites, many=True)
        
        return Response({
            'success': True,
            'favorites': serializer.data,
            'total': favorites.count()
        })
    
    elif request.method == 'POST':
        data = request.data.copy()
        
        # Check if already favorited
        existing = FavoriteQuote.objects.filter(
            user=request.user,
            quote_text=data.get('quote_text')
        ).exists()
        
        if existing:
            return Response({
                'success': False,
                'error': 'Quote already in favorites'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = FavoriteQuoteSerializer(data=data)
        
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({
                'success': True,
                'favorite': serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_favorite(request, favorite_id):
    """Delete a favorite quote"""
    try:
        favorite = FavoriteQuote.objects.get(id=favorite_id, user=request.user)
        favorite.delete()
        
        return Response({
            'success': True,
            'message': 'Favorite removed'
        })
    except FavoriteQuote.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Favorite not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat_with_quotes(request):
    """RAG-powered conversational quote search"""
    query = request.data.get('query', '').strip()
    username = request.data.get('username')
    accent = request.data.get('accent', 'american')
    
    if not query:
        return Response({
            'success': False,
            'error': 'Query required'
        }, status=400)
    
    try:
        # Initialize RAG chatbot
        chatbot = RAGChatbot(
            neo4j_uri=NEO4J_URI,
            neo4j_user=NEO4J_USER,
            neo4j_password=NEO4J_PASSWORD,
            llm_provider="ollama",  # or make this configurable
            llm_config={'model': 'llama3.2:3b'}
        )
        
        # Get RAG response
        result = chatbot.query(query, username, accent)
        chatbot.close()
        
        return Response({
            'success': True,
            'response': result['response'],
            'quotes': result['quotes'],
            'method': result['method']
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)
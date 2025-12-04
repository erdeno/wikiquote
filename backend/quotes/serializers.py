from rest_framework import serializers
from .models import QueryHistory, FavoriteQuote

class QueryHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = QueryHistory
        fields = ['id', 'query_text', 'results_found', 'timestamp']
        read_only_fields = ['timestamp']


class FavoriteQuoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteQuote
        fields = ['id', 'quote_text', 'author', 'work', 'saved_at', 'notes']
        read_only_fields = ['saved_at']
from django.db import models
from django.contrib.auth.models import User

class QueryHistory(models.Model):
    """Track user quote searches"""
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='query_history',
        null=True,  # ✓ Add this
        blank=True  # ✓ Add this
    )
    query_text = models.TextField()
    results_found = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)


class FavoriteQuote(models.Model):
    """User's favorite quotes"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_quotes')
    quote_text = models.TextField()
    author = models.CharField(max_length=255)
    work = models.CharField(max_length=255, blank=True, null=True)
    neo4j_id = models.CharField(max_length=100, blank=True, null=True)  # Store Neo4j node ID
    saved_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)  # Personal notes
    
    class Meta:
        db_table = 'favorite_quotes'
        ordering = ['-saved_at']
        unique_together = ['user', 'quote_text']  # Prevent duplicate favorites
    
    def __str__(self):
        return f"{self.user.username}: {self.author}"
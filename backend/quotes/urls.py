from django.urls import path, include
from . import views

urlpatterns = [
    path("healthz", views.healthz),
    path('search/', views.search_quotes),
    path('history/', views.get_query_history),
    path('history/clear/', views.clear_query_history),
    path('favorites/', views.favorite_quotes),
    path('favorites/<int:favorite_id>/', views.delete_favorite),
    path("chat/", views.chat_with_quotes),
]

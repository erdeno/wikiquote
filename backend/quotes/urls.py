from django.urls import path, include
from . import views

urlpatterns = [
    path("healthz", views.healthz),
    path("api/v1/", include("backend.api_v1.urls")),
]

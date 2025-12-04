from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/v1/auth/', include('backend.accounts.urls')),
    path("api/v1/", include("backend.api_v1.urls")),
    path("api/v1/voice/", include("backend.voice.urls")),
    path("api/v1/quotes/", include("backend.quotes.urls")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
from django.urls import path, include

urlpatterns = [
    # Include all quote endpoints from quotes app
    path("quotes/", include("backend.quotes.urls")),
    
    # Future dialog endpoints
    # path("dialog/", include("dialog.urls")),
]
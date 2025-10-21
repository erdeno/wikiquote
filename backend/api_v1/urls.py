from django.urls import path, include
from rest_framework.routers import SimpleRouter

from backend.quotes.views import QuoteViewSet
# from dialog.views import which_quote  # if you already created dialog app/views

router = SimpleRouter()
router.register(r"quotes", QuoteViewSet, basename="quotes")

urlpatterns = [
    # router-driven endpoints (list/retrieve/custom actions under /quotes/)
    path("", include(router.urls)),

    # bespoke endpoints that don't fit a ViewSet
    # path("dialog/which-quote", which_quote),
]

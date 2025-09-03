from rest_framework.routers import DefaultRouter
from .views import ChatSessionViewSet, MessageViewSet

router = DefaultRouter()
router.register(r'sessions', ChatSessionViewSet, basename='chat-session')
router.register(r'messages', MessageViewSet, basename='chat-message')

urlpatterns = router.urls



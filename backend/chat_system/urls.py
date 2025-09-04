from rest_framework.routers import DefaultRouter
from .views import ChatSessionViewSet, MessageViewSet
from .memory_views import UserMemoryViewSet

router = DefaultRouter()
router.register(r'sessions', ChatSessionViewSet, basename='chat-session')
router.register(r'messages', MessageViewSet, basename='chat-message')
router.register(r'memories', UserMemoryViewSet, basename='user-memory')

urlpatterns = router.urls



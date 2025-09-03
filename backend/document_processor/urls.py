from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DocumentViewSet, LearningPackageViewSet

router = DefaultRouter()
router.register(r'documents', DocumentViewSet, basename='document')
router.register(r'packages', LearningPackageViewSet, basename='package')

urlpatterns = [
    path('', include(router.urls)),
]

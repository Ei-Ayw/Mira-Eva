from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import UserSettings
from .serializers import UserSettingsSerializer


class UserSettingsViewSet(viewsets.ModelViewSet):
    queryset = UserSettings.objects.all()
    serializer_class = UserSettingsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserSettings.objects.filter(user=self.request.user)

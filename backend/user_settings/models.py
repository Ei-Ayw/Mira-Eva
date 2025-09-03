from django.db import models
from django.contrib.auth.models import User


class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')
    proactive_enabled = models.BooleanField(default=True)

    def __str__(self):
        return f"settings-{self.user.username}"



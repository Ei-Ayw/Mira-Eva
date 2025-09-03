from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.CharField(max_length=200, blank=True, default='')
    avatar = models.URLField(blank=True, default='')

    def __str__(self):
        return self.user.username



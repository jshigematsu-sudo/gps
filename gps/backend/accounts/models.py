from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


class CustomUser(AbstractUser):
    """拡張ユーザーモデル"""

    token = models.CharField(max_length=36, default=uuid.uuid4, unique=True)

    class Meta:
        verbose_name_plural = 'CustomUser'

    def __str__(self):
        return self.username

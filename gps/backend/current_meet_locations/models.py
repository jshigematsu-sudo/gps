import uuid

from django.core.exceptions import ValidationError
from django.db import models


class User(models.Model):
    name = models.CharField(max_length=255)  # ユーザーの名前
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)  # UUIDのtoken

    def __str__(self):
        return f"{self.name} - {self.token}"


class Location(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=False)

    # UserのtokenをForeignKeyにする
    user = models.ForeignKey(User, to_field="token", on_delete=models.CASCADE, db_column="user_token")

    def __str__(self):
        return f"{self.latitude}, {self.longitude} - User Token: {self.user.token}"


class Sites(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    date_range = models.IntegerField(blank=False, null=False)

class SiteMembers(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    site = models.ForeignKey(Sites, on_delete=models.CASCADE, related_name='members')
    name = models.CharField(max_length=255)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['site', 'name'], name='unique_site_name_constraint'),
        ]

    def __str__(self):
        return f"Site: {self.site} - Name: {self.name}"


class MembersLocations(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    site_member = models.ForeignKey(SiteMembers, on_delete=models.CASCADE, related_name='locations')

    def clean(self):
        if not -90 <= self.latitude <= 90:
            raise ValidationError('緯度は-90から90の範囲である必要があります')
        if not -180 <= self.longitude <= 180:
            raise ValidationError('経度は-180から180の範囲である必要があります')

class MeetingChats(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    site_member = models.ForeignKey(SiteMembers, on_delete=models.CASCADE, related_name='chats')
    site = models.ForeignKey(Sites, on_delete=models.CASCADE, related_name='chats')
    message = models.TextField(blank=False, null=False)
    timestamp = models.DateTimeField(auto_now_add=True)

class MeetingChats(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    site = models.ForeignKey(Sites, on_delete=models.CASCADE, related_name='chats')
    site_member = models.ForeignKey(SiteMembers, on_delete=models.CASCADE, related_name='chats')
    message = models.TextField(blank=False, null=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"[{self.timestamp}] {self.site_member.name}: {self.message}"
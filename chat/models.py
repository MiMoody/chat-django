from django.db import models
from django.contrib.auth.models import User


class Room(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    current_users = models.ManyToManyField(User, related_name="current_rooms", blank=True)

    def __str__(self):
        return f"Room({self.name})"


class Message(models.Model):
    room = models.ForeignKey("chat.Room", on_delete=models.CASCADE, related_name="messages")
    text = models.TextField(max_length=500)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message({self.user} {self.room})"

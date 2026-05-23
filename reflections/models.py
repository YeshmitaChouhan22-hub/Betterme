from django.db import models
from django.contrib.auth.models import User

class DailyReflection(models.Model):
    EMOTION_CHOICES = [
        ('happy', 'Happy'),
        ('calm', 'Calm'),
        ('stressed', 'Stressed'),
        ('motivated', 'Motivated'),
        ('tired', 'Tired'),
        ('peaceful', 'Peaceful'),
        ('emotional', 'Emotional'),
        ('relaxed', 'Relaxed'),
    ]

    ACTIVITY_CHOICES = [
        ('worked', 'Worked'),
        ('studied', 'Studied'),
        ('exercised', 'Exercised'),
        ('rested', 'Rested'),
        ('watched_movies', 'Watched Movies'),
        ('socialized', 'Socialized'),
        ('self_care', 'Self-care'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    emotion = models.CharField(max_length=20, choices=EMOTION_CHOICES)
    activity = models.CharField(max_length=20, choices=ACTIVITY_CHOICES)
    affirmation = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} felt {self.emotion} on {self.created_at.strftime('%Y-%m-%d')}"
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Conversation(models.Model):
    LANGUAGE_CHOICES = [
        ('fa', 'Persian'),
        ('en', 'English'),
        ('both', 'Bilingual'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    language = models.CharField(
        max_length=10, 
        choices=LANGUAGE_CHOICES,
        default='both'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    is_bot = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{'Bot' if self.is_bot else 'User'}: {self.content[:50]}"

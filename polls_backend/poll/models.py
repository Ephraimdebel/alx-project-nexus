# poll/models.py
from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL  # compatible if you use a custom user

class Poll(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="polls")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title
    class Meta:
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['expires_at']),
        ]

class Question(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="questions")
    text = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.poll.title} - {self.text}"

    class Meta:
        indexes = [
            models.Index(fields=['created_at']),
        ]

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    text = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.question.text} -> {self.text}"


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="votes")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="votes")
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE, related_name="votes")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} -> {self.question} = {self.choice}"
    
    class Meta:
        unique_together = ('user', 'question') # ONE vote per user per question
        indexes = [
            models.Index(fields=['question']),
            models.Index(fields=['choice']),
            models.Index(fields=['user']),
        ]
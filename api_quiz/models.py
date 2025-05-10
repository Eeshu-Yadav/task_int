from django.db import models
from django.contrib.auth import get_user_model
import json
from django.db.models import JSONField
User = get_user_model()

class Couple(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='couple_user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='couple_user2')
    created_at = models.DateTimeField(auto_now_add=True)

    # class Meta:
    #     unique_together = ('user1', 'user2')

class ChatKeyword(models.Model):
    couple = models.ForeignKey(Couple, on_delete=models.CASCADE)
    keyword = models.CharField(max_length=100)
    frequency = models.IntegerField(default=1)
    last_used = models.DateTimeField(auto_now=True)
    is_phrase = models.BooleanField(default=False) 

    class Meta:
        unique_together = ('couple', 'keyword')

class QuizTemplate(models.Model):
    TEMPLATE_CHOICES = [
        ('MCQ', 'Multiple Choice'),
        ('SLIDER', 'Slider Scale'),
        ('BINARY', 'Binary Choice'),
        ('SHORT', 'Short Answer')
        
    ]
    name = models.CharField(max_length=100)
    template_type = models.CharField(max_length=10, choices=TEMPLATE_CHOICES)
    system_prompt = models.TextField()
    example_json = models.JSONField()


class QuizQuestion(models.Model):
    couple = models.ForeignKey(Couple, on_delete=models.CASCADE)
    template = models.ForeignKey(QuizTemplate, on_delete=models.CASCADE)
    question_data = JSONField()
    # keywords = models.JSONField()
    source_keywords = JSONField()
    created_at = models.DateTimeField(auto_now_add=True)


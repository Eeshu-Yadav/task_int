from rest_framework import serializers
from .models import GameSuggestion, QuizQuestion

class QuizQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizQuestion
        fields = ['id', 'question_text', 'options', 'correct_answer', 'explanation']

class GameSuggestionSerializer(serializers.ModelSerializer):
    questions = QuizQuestionSerializer(many=True, read_only=True)
    
    class Meta:
        model = GameSuggestion
        fields = ['id', 'game_type', 'suggested_at', 'completed', 'completed_at', 'questions']
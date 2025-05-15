# from rest_framework import serializers
# from .models import GameSuggestion, QuizQuestion

# class QuizQuestionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = QuizQuestion
#         fields = ['id', 'question_text', 'options', 'correct_answer', 'explanation']

# class GameSuggestionSerializer(serializers.ModelSerializer):
#     questions = QuizQuestionSerializer(many=True, read_only=True)
    
#     class Meta:
#         model = GameSuggestion
#         fields = ['id', 'game_type', 'suggested_at', 'completed', 'completed_at', 'questions']

from rest_framework import serializers
from .models import QuizQuestion, RelationshipAssessment

class AnswerSerializer(serializers.Serializer):
    question_text = serializers.CharField()
    answer = serializers.CharField()

class QuizResultInputSerializer(serializers.Serializer):
    quiz_id = serializers.IntegerField()
    answers = serializers.ListSerializer(
        child=AnswerSerializer(),
        allow_empty=False
    )

class RelationshipAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RelationshipAssessment
        fields = [
            'state',
            'open_communication',
            'trust',
            'individuality',
            'curiosity',
            'time_apart',
            'playfulness',
            'physical_intimacy',
        ]

class QuizQuestionSerializer(serializers.ModelSerializer):
    questions = serializers.SerializerMethodField()
    template = serializers.CharField(source='template.name')
    keywords = serializers.ListField(source='source_keywords')
    quiz_id = serializers.IntegerField(source='id')

    class Meta:
        model = QuizQuestion
        fields = ['quiz_id', 'questions', 'template', 'keywords']

    def get_questions(self, obj):
        return obj.question_data.get('questions', [])

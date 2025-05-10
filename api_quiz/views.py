# from django.db import models
# from rest_framework import status
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from rest_framework.permissions import IsAuthenticated
# from .models import Couple, GameSuggestion
# from .services import GameSuggestionService, QuizGeneratorService
# import logging

# logger = logging.getLogger(__name__)

# class GameSuggestionsView(APIView):
#     permission_classes = [IsAuthenticated]
    
#     def get(self, request):
#         try:
#             couple = Couple.objects.get(
#                 models.Q(user1=request.user) | models.Q(user2=request.user)
#             )
#             suggestions = GameSuggestionService.create_game_suggestions(couple.id)
#             return Response({
#                 'status': 'success',
#                 'suggestions': [
#                     {
#                         'id': s.id,
#                         'game_type': s.game_type.name,
#                         'suggested_at': s.suggested_at
#                     } for s in suggestions
#                 ]
#             }, status=status.HTTP_200_OK)
#         except Couple.DoesNotExist:
#             return Response({
#                 'status': 'error',
#                 'message': 'No couple found for this user'
#             }, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             logger.error(f"Error generating game suggestions: {str(e)}")
#             return Response({
#                 'status': 'error',
#                 'message': 'Failed to generate game suggestions'
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class QuizQuestionsView(APIView):
#     permission_classes = [IsAuthenticated]
    
#     def get(self, request, suggestion_id):
#         try:
#             # Verify the user has access to this suggestion
#             couple = Couple.objects.get(
#                 models.Q(user1=request.user) | models.Q(user2=request.user)
#             )
#             suggestion = GameSuggestion.objects.get(
#                 id=suggestion_id,
#                 couple=couple
#             )
            
#             # Generate or get existing questions
#             if not suggestion.questions.exists():
#                 QuizGeneratorService.generate_quiz_questions(suggestion.id)
                
#             questions = suggestion.questions.all()
#             return Response({
#                 'status': 'success',
#                 'questions': [
#                     {
#                         'id': q.id,
#                         'question_text': q.question_text,
#                         'options': q.options,
#                         'correct_answer': q.correct_answer,
#                         'explanation': q.explanation
#                     } for q in questions
#                 ]
#             }, status=status.HTTP_200_OK)
#         except (Couple.DoesNotExist, GameSuggestion.DoesNotExist):
#             return Response({
#                 'status': 'error',
#                 'message': 'Not found'
#             }, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             logger.error(f"Error generating quiz questions: {str(e)}")
#             return Response({
#                 'status': 'error',
#                 'message': 'Failed to generate quiz questions'
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import QuizGenerator

class QuizView(APIView):
    def get(self, request, couple_id):
        template_type = request.query_params.get('type', 'MCQ')
        try:
            quiz = QuizGenerator.generate_quiz(couple_id, template_type)
            if not quiz:
                return Response(
                    {"error": "Failed to generate quiz"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
            return Response({
                'questions': quiz.question_data['questions'],
                'template': quiz.template.name,
                'keywords': quiz.keywords.split(',')
            })
            
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
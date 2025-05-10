from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import QuizGenerator, KeywordManager

class QuizView(APIView):
    def get(self, request, couple_id):
        template_type = request.query_params.get('type')
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
                'keywords': quiz.source_keywords
            })
            
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
class ProcessChatView(APIView):
    def post(self, request, couple_id):
        message = request.data.get('message')
        if not message:
            return Response(
                {"error": "Message required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            KeywordManager.update_keywords(couple_id, message)
            return Response({
                "status": "Keywords updated",
                "details": f"Processed message for couple {couple_id}"
            })
        except Exception as e:
            return Response(
                {"error": f"Keyword update failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
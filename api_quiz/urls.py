from django.urls import path
# from .views import GameSuggestionsView, QuizQuestionsView
from .views import QuizView, ProcessChatView

urlpatterns = [
    path('quiz/<int:couple_id>/', QuizView.as_view(), name='couple-quiz'),
    path('process-chat/<int:couple_id>/', ProcessChatView.as_view(), name='process-chat'),
]
# urlpatterns = [
#     # path('game_suggestions/', GameSuggestionsView.as_view(), name='game-suggestions'),
#     # path('quiz-questions/<int:suggestion_id>/', QuizQuestionsView.as_view(), name='quiz-questions'),
# ]
from django.urls import path
# from .views import GameSuggestionsView, QuizQuestionsView
from .views import QuizView

urlpatterns = [
    path('quiz/<int:couple_id>/', QuizView.as_view(), name='couple-quiz'),
]
# urlpatterns = [
#     # path('game_suggestions/', GameSuggestionsView.as_view(), name='game-suggestions'),
#     # path('quiz-questions/<int:suggestion_id>/', QuizQuestionsView.as_view(), name='quiz-questions'),
# ]
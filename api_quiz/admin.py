# admin.py
from django.contrib import admin
from .models import QuizTemplate, QuizQuestion
# from .models import Couple, ChatKeyword, GameType, GameSuggestion, QuizQuestion

# @admin.register(Couple)
# class CoupleAdmin(admin.ModelAdmin):
#     list_display = ('id', 'user1', 'user2', 'created_at')
#     search_fields = ('user1__username', 'user2__username')

# @admin.register(ChatKeyword)
# class ChatKeywordAdmin(admin.ModelAdmin):
#     list_display = ('couple', 'keyword', 'frequency', 'last_updated')
#     list_filter = ('couple',)
#     search_fields = ('keyword',)

# @admin.register(GameType)
# class GameTypeAdmin(admin.ModelAdmin):
#     list_display = ('name', 'description', 'is_active')
#     search_fields = ('name',)

# @admin.register(GameSuggestion)
# class GameSuggestionAdmin(admin.ModelAdmin):
#     list_display = ('couple', 'game_type', 'suggested_at', 'completed')
#     list_filter = ('game_type', 'completed')
#     search_fields = ('couple__user1__username', 'couple__user2__username')

# @admin.register(QuizQuestion)
# class QuizQuestionAdmin(admin.ModelAdmin):
#     list_display = ('game_suggestion', 'question_text')
#     search_fields = ('question_text',)
#     list_filter = ('game_suggestion',)


@admin.register(QuizTemplate)
class QuizTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'template_type')
    readonly_fields = ('example_json_preview',)
    
    def example_json_preview(self, obj):
        return obj.example_json

@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ('couple', 'template', 'created_at')
    search_fields = ('keywords',)
    readonly_fields = ('question_data_preview',)
    
    def question_data_preview(self, obj):
        return obj.question_data
from django.contrib import admin
from .models import (
    VocabularyCategory, Word, GrammarTopic,
    Exercise, ExerciseQuestion, ExerciseResult,
    UserWordProgress, UserGrammarProgress,
    InterestCategory, InterestQuestion, InterestResult,
    LogicExercise, LogicQuestion, LogicResult,
)


@admin.register(VocabularyCategory)
class VocabularyCategoryAdmin(admin.ModelAdmin):
    list_display = ['icon', 'name', 'name_uz', 'level', 'word_count', 'order']
    list_filter = ['level']
    search_fields = ['name', 'name_uz']
    ordering = ['order', 'name']

    def word_count(self, obj):
        return obj.words.count()
    word_count.short_description = 'So\'zlar soni'


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ['english', 'uzbek', 'pronunciation', 'level', 'category']
    list_filter = ['level', 'category']
    search_fields = ['english', 'uzbek']
    ordering = ['category', 'english']


@admin.register(GrammarTopic)
class GrammarTopicAdmin(admin.ModelAdmin):
    list_display = ['icon', 'title', 'title_uz', 'level', 'order']
    list_filter = ['level']
    search_fields = ['title', 'title_uz']
    ordering = ['level', 'order']


class ExerciseQuestionInline(admin.TabularInline):
    model = ExerciseQuestion
    extra = 1
    fields = ['question_text', 'correct_answer', 'points', 'order']


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ['title', 'exercise_type', 'category', 'level', 'is_active', 'created_date']
    list_filter = ['exercise_type', 'category', 'level', 'is_active']
    search_fields = ['title']
    inlines = [ExerciseQuestionInline]


@admin.register(ExerciseQuestion)
class ExerciseQuestionAdmin(admin.ModelAdmin):
    list_display = ['exercise', 'question_text', 'correct_answer', 'points', 'order']
    list_filter = ['exercise__exercise_type', 'exercise__category']
    search_fields = ['question_text', 'correct_answer']


@admin.register(ExerciseResult)
class ExerciseResultAdmin(admin.ModelAdmin):
    list_display = ['user', 'exercise', 'score', 'total_questions', 'completed_date']
    list_filter = ['exercise__category', 'completed_date']
    search_fields = ['user__username']
    readonly_fields = ['completed_date']


@admin.register(UserWordProgress)
class UserWordProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'word', 'learned', 'review_count', 'last_review']
    list_filter = ['learned']
    search_fields = ['user__username', 'word__english']


@admin.register(UserGrammarProgress)
class UserGrammarProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'grammar_topic', 'completed', 'score']
    list_filter = ['completed']
    search_fields = ['user__username', 'grammar_topic__title']


# ============ QIZIQISHLAR ADMIN ============

@admin.register(InterestCategory)
class InterestCategoryAdmin(admin.ModelAdmin):
    list_display = ['icon', 'name', 'order']
    search_fields = ['name']
    ordering = ['order']


@admin.register(InterestQuestion)
class InterestQuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'question_type', 'order', 'is_active']
    list_filter = ['question_type', 'is_active']
    search_fields = ['question_text']
    ordering = ['order']


@admin.register(InterestResult)
class InterestResultAdmin(admin.ModelAdmin):
    list_display = ['user', 'top_category', 'age', 'completed_date']
    list_filter = ['top_category', 'completed_date']
    readonly_fields = ['completed_date']


# ============ MANTIQIY MASHQLAR ADMIN ============

class LogicQuestionInline(admin.TabularInline):
    model = LogicQuestion
    extra = 1
    fields = ['question_text', 'correct_answer', 'points', 'order']


@admin.register(LogicExercise)
class LogicExerciseAdmin(admin.ModelAdmin):
    list_display = ['icon', 'title', 'exercise_type', 'difficulty', 'is_active', 'question_count']
    list_filter = ['exercise_type', 'difficulty', 'is_active']
    search_fields = ['title']
    inlines = [LogicQuestionInline]

    def question_count(self, obj):
        return obj.logic_questions.count()
    question_count.short_description = 'Savollar'


@admin.register(LogicQuestion)
class LogicQuestionAdmin(admin.ModelAdmin):
    list_display = ['exercise', 'question_text', 'correct_answer', 'points', 'order']
    list_filter = ['exercise__exercise_type', 'exercise__difficulty']
    search_fields = ['question_text', 'correct_answer']


@admin.register(LogicResult)
class LogicResultAdmin(admin.ModelAdmin):
    list_display = ['user', 'exercise', 'score', 'total_questions', 'completed_date']
    list_filter = ['exercise', 'completed_date']
    readonly_fields = ['completed_date']

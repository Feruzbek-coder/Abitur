from django.urls import path
from . import views

app_name = 'edukids'

urlpatterns = [
    # Bosh sahifa
    path('', views.home, name='home'),

    # Vocabulary
    path('vocabulary/', views.vocabulary_index, name='vocabulary_index'),
    path('vocabulary/<int:category_id>/', views.vocabulary_words, name='vocabulary_words'),
    path('vocabulary/<int:category_id>/flashcards/', views.vocabulary_flashcards, name='vocabulary_flashcards'),
    path('vocabulary/search/', views.vocabulary_search, name='vocabulary_search'),
    path('vocabulary/word/<int:word_id>/learned/', views.mark_word_learned, name='mark_word_learned'),

    # Grammar
    path('grammar/', views.grammar_index, name='grammar_index'),
    path('grammar/<int:topic_id>/', views.grammar_topic_detail, name='grammar_topic_detail'),
    path('grammar/<int:topic_id>/complete/', views.mark_grammar_complete, name='mark_grammar_complete'),

    # Exercises
    path('exercises/', views.exercises_index, name='exercises_index'),
    path('exercises/grammar/', views.grammar_exercises, name='grammar_exercises'),
    path('exercises/vocabulary/', views.vocabulary_exercises, name='vocabulary_exercises'),
    path('exercises/<int:exercise_id>/play/', views.exercise_play, name='exercise_play'),
    path('exercises/<int:exercise_id>/submit/', views.exercise_submit, name='exercise_submit'),

    # Qiziqishlarni aniqlash (9-14 yosh)
    path('interests/', views.interests_home, name='interests_home'),
    path('interests/quiz/', views.interests_quiz, name='interests_quiz'),
    path('interests/submit/', views.interests_submit, name='interests_submit'),
    path('interests/result/<int:result_id>/', views.interests_result, name='interests_result'),

    # Mantiqiy fikrlash (9-14 yosh)
    path('logic/', views.logic_home, name='logic_home'),
    path('logic/<int:exercise_id>/play/', views.logic_exercise_play, name='logic_exercise_play'),
    path('logic/<int:exercise_id>/submit/', views.logic_submit, name='logic_submit'),
]

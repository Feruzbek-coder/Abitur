import json
import random
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone

from .models import (
    VocabularyCategory, Word, GrammarTopic, Exercise,
    ExerciseQuestion, ExerciseResult, UserWordProgress, UserGrammarProgress,
    InterestCategory, InterestQuestion, InterestResult,
    LogicExercise, LogicQuestion, LogicResult,
)


# ============ BOSH SAHIFA ============

def home(request):
    """EduKids bosh sahifasi"""
    vocab_categories = VocabularyCategory.objects.all()[:4]
    grammar_topics = GrammarTopic.objects.order_by('order')[:4]
    stats = {
        'vocab_count': VocabularyCategory.objects.count(),
        'grammar_count': GrammarTopic.objects.count(),
        'exercise_count': Exercise.objects.filter(is_active=True).count(),
    }
    return render(request, 'exams/edukids/home.html', {
        'vocab_categories': vocab_categories,
        'grammar_topics': grammar_topics,
        'stats': stats,
    })


# ============ VOCABULARY VIEWS ============

def vocabulary_index(request):
    """Vocabulary kategoriyalar ro'yxati"""
    categories = VocabularyCategory.objects.all()
    return render(request, 'exams/edukids/vocabulary/index.html', {
        'categories': categories,
    })


def vocabulary_words(request, category_id):
    """Kategoriya ichidagi so'zlar"""
    category = get_object_or_404(VocabularyCategory, id=category_id)
    words = Word.objects.filter(category=category)

    user_progress = {}
    if request.user.is_authenticated:
        progress = UserWordProgress.objects.filter(user=request.user)
        user_progress = {p.word_id: p.learned for p in progress}

    return render(request, 'exams/edukids/vocabulary/words.html', {
        'category': category,
        'words': words,
        'user_progress': user_progress,
    })


def vocabulary_flashcards(request, category_id):
    """Flashcard rejimida so'zlarni o'rganish"""
    category = get_object_or_404(VocabularyCategory, id=category_id)
    words = list(Word.objects.filter(category=category))
    return render(request, 'exams/edukids/vocabulary/flashcards.html', {
        'category': category,
        'words': words,
    })


@login_required
@require_POST
def mark_word_learned(request, word_id):
    """So'zni o'rganilgan deb belgilash"""
    word = get_object_or_404(Word, id=word_id)
    progress, created = UserWordProgress.objects.get_or_create(
        user=request.user, word=word,
        defaults={'learned': True, 'review_count': 1}
    )
    if not created:
        progress.learned = True
        progress.review_count += 1
        progress.last_review = timezone.now()
        progress.save()
    return JsonResponse({'success': True})


def vocabulary_search(request):
    """So'z qidirish (AJAX)"""
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse([], safe=False)
    words = Word.objects.filter(
        english__icontains=query
    ) | Word.objects.filter(uzbek__icontains=query)
    words = words[:20]
    return JsonResponse([{
        'id': w.id,
        'english': w.english,
        'uzbek': w.uzbek,
        'level': w.level,
        'category': w.category.name,
    } for w in words], safe=False)


# ============ GRAMMAR VIEWS ============

def grammar_index(request):
    """Grammar mavzular ro'yxati"""
    topics = GrammarTopic.objects.order_by('level', 'order')
    user_progress = {}
    if request.user.is_authenticated:
        progress = UserGrammarProgress.objects.filter(user=request.user)
        user_progress = {p.grammar_topic_id: p.completed for p in progress}
    return render(request, 'exams/edukids/grammar/index.html', {
        'topics': topics,
        'user_progress': user_progress,
    })


def grammar_topic_detail(request, topic_id):
    """Grammar mavzusi tafsilotlari"""
    topic = get_object_or_404(GrammarTopic, id=topic_id)
    prev_topic = GrammarTopic.objects.filter(
        level=topic.level, order__lt=topic.order
    ).order_by('-order').first()
    next_topic = GrammarTopic.objects.filter(
        level=topic.level, order__gt=topic.order
    ).order_by('order').first()
    exercises = topic.exercises.filter(is_active=True)
    completed = False
    if request.user.is_authenticated:
        completed = UserGrammarProgress.objects.filter(
            user=request.user, grammar_topic=topic, completed=True
        ).exists()
    return render(request, 'exams/edukids/grammar/topic.html', {
        'topic': topic,
        'prev_topic': prev_topic,
        'next_topic': next_topic,
        'exercises': exercises,
        'completed': completed,
    })


@login_required
@require_POST
def mark_grammar_complete(request, topic_id):
    """Mavzuni o'qilgan deb belgilash"""
    topic = get_object_or_404(GrammarTopic, id=topic_id)
    progress, created = UserGrammarProgress.objects.get_or_create(
        user=request.user, grammar_topic=topic,
        defaults={'completed': True}
    )
    if not created:
        progress.completed = True
        progress.save()
    return JsonResponse({'success': True})


# ============ EXERCISE VIEWS ============

def exercises_index(request):
    """Mashqlar bosh sahifasi"""
    exercise_types = [
        {'type': 'multiple_choice', 'name': 'Test savollari', 'icon': '✅',
         'description': 'To\'g\'ri javobni tanlang', 'color': 'primary'},
        {'type': 'fill_gaps', 'name': "Bo'sh joy to'ldirish", 'icon': '📝',
         'description': 'Bo\'sh joylarga to\'g\'ri so\'zni kiriting', 'color': 'success'},
        {'type': 'matching', 'name': 'Moslashtirish', 'icon': '🔗',
         'description': 'So\'zlarni tarjimalari bilan moslang', 'color': 'info'},
        {'type': 'word_search', 'name': 'So\'z qidirish', 'icon': '🔍',
         'description': 'Harflar orasida yashiringan so\'zlarni toping', 'color': 'warning'},
        {'type': 'word_scramble', 'name': 'Harflarni joylashtiring', 'icon': '🔤',
         'description': 'Aralashtirilgan harflardan so\'z tuzing', 'color': 'danger'},
    ]
    grammar_count = Exercise.objects.filter(category='grammar', is_active=True).count()
    vocab_count = Exercise.objects.filter(category='vocabulary', is_active=True).count()
    return render(request, 'exams/edukids/exercises/index.html', {
        'exercise_types': exercise_types,
        'grammar_count': grammar_count,
        'vocab_count': vocab_count,
    })


def grammar_exercises(request):
    """Grammar mashqlari ro'yxati"""
    exercise_type = request.GET.get('type', None)
    exercises = Exercise.objects.filter(category='grammar', is_active=True)
    if exercise_type:
        exercises = exercises.filter(exercise_type=exercise_type)
    return render(request, 'exams/edukids/exercises/grammar_list.html', {
        'exercises': exercises,
        'selected_type': exercise_type,
    })


def vocabulary_exercises(request):
    """Vocabulary mashqlari ro'yxati"""
    exercise_type = request.GET.get('type', None)
    exercises = Exercise.objects.filter(category='vocabulary', is_active=True)
    if exercise_type:
        exercises = exercises.filter(exercise_type=exercise_type)
    return render(request, 'exams/edukids/exercises/vocabulary_list.html', {
        'exercises': exercises,
        'selected_type': exercise_type,
    })


def exercise_play(request, exercise_id):
    """Mashqni bajarish"""
    exercise = get_object_or_404(Exercise, id=exercise_id, is_active=True)
    questions = ExerciseQuestion.objects.filter(exercise=exercise).order_by('order')

    # Word Search uchun random savol tanlash
    if exercise.exercise_type == 'word_search' and questions.count() > 1:
        questions = [random.choice(list(questions))]
    else:
        questions = list(questions)

    questions_data = []
    for q in questions:
        q_data = {
            'id': q.id,
            'question_text': q.question_text,
            'correct_answer': q.correct_answer,
            'points': q.points,
        }
        if q.options:
            try:
                q_data['options'] = json.loads(q.options)
            except (json.JSONDecodeError, TypeError):
                q_data['options'] = []
        if q.gap_text:
            q_data['gap_text'] = q.gap_text
        if q.matching_pairs:
            try:
                q_data['matching_pairs'] = json.loads(q.matching_pairs)
            except (json.JSONDecodeError, TypeError):
                q_data['matching_pairs'] = {'left': [], 'right': []}
        if q.word_grid:
            try:
                q_data['word_grid'] = json.loads(q.word_grid)
            except (json.JSONDecodeError, TypeError):
                q_data['word_grid'] = []
        if q.hidden_words:
            try:
                q_data['hidden_words'] = json.loads(q.hidden_words)
            except (json.JSONDecodeError, TypeError):
                q_data['hidden_words'] = []
        questions_data.append(q_data)

    template_map = {
        'multiple_choice': 'exams/edukids/exercises/play/multiple_choice.html',
        'fill_gaps': 'exams/edukids/exercises/play/fill_gaps.html',
        'matching': 'exams/edukids/exercises/play/matching.html',
        'word_search': 'exams/edukids/exercises/play/word_search.html',
        'word_scramble': 'exams/edukids/exercises/play/word_scramble.html',
    }
    template = template_map.get(exercise.exercise_type, 'exams/edukids/exercises/play/multiple_choice.html')

    return render(request, template, {
        'exercise': exercise,
        'questions': questions,
        'questions_json': json.dumps(questions_data, ensure_ascii=False),
    })


def exercise_submit(request, exercise_id):
    """Mashq natijasini saqlash (AJAX POST)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST kerak'}, status=405)
    exercise = get_object_or_404(Exercise, id=exercise_id)
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, Exception):
        return JsonResponse({'error': 'Noto\'g\'ri so\'rov'}, status=400)

    score = int(data.get('score', 0))
    total = int(data.get('total', 0))
    time_spent = int(data.get('time_spent', 0))

    if request.user.is_authenticated:
        ExerciseResult.objects.create(
            user=request.user,
            exercise=exercise,
            score=score,
            total_questions=total,
            time_spent=time_spent,
        )

    percentage = round(score / total * 100) if total > 0 else 0
    return JsonResponse({
        'success': True,
        'score': score,
        'total': total,
        'percentage': percentage,
    })


# ============ QIZIQISHLARNI ANIQLASH (9-14 YOŠ) ============

def interests_home(request):
    """Qiziqishlarni aniqlash bosh sahifasi"""
    categories = InterestCategory.objects.all()
    total_questions = InterestQuestion.objects.filter(is_active=True).count()
    last_result = None
    if request.user.is_authenticated:
        last_result = InterestResult.objects.filter(user=request.user).first()
    return render(request, 'exams/edukids/interests/home.html', {
        'categories': categories,
        'total_questions': total_questions,
        'last_result': last_result,
    })


def interests_quiz(request):
    """Qiziqishlarni aniqlash testi"""
    questions = list(InterestQuestion.objects.filter(is_active=True).order_by('order'))
    categories = InterestCategory.objects.all()
    questions_data = []
    for q in questions:
        questions_data.append({
            'id': q.id,
            'text': q.question_text,
            'type': q.question_type,
            'options': q.get_options(),
        })
    return render(request, 'exams/edukids/interests/quiz.html', {
        'questions': questions,
        'categories': categories,
        'questions_json': json.dumps(questions_data, ensure_ascii=False),
    })


def interests_submit(request):
    """Test natijalarini hisoblash va saqlash"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST kerak'}, status=405)
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': "Noto'g'ri so'rov"}, status=400)

    answers = data.get('answers', {})
    age = data.get('age', None)

    questions = InterestQuestion.objects.filter(is_active=True)
    category_scores = {}
    for cat in InterestCategory.objects.all():
        category_scores[cat.name] = 0

    for q in questions:
        answer_key = str(q.id)
        if answer_key not in answers:
            continue
        options = q.get_options()
        if q.question_type == 'single':
            chosen_idx = answers[answer_key]
            if isinstance(chosen_idx, int) and 0 <= chosen_idx < len(options):
                weights = options[chosen_idx].get('weights', {})
                for cat_name, pts in weights.items():
                    if cat_name in category_scores:
                        category_scores[cat_name] += pts
        elif q.question_type == 'scale':
            scale_val = int(answers[answer_key]) if answers[answer_key] else 0
            weights = options[0].get('weights', {}) if options else {}
            for cat_name, pts in weights.items():
                if cat_name in category_scores:
                    category_scores[cat_name] += pts * scale_val

    top_name = max(category_scores, key=category_scores.get) if category_scores else None
    top_cat = InterestCategory.objects.filter(name=top_name).first() if top_name else None

    result = InterestResult(
        scores=json.dumps(category_scores, ensure_ascii=False),
        top_category=top_cat,
        age=age,
    )
    if request.user.is_authenticated:
        result.user = request.user
    else:
        session_key = request.session.session_key or ''
        result.session_key = session_key
    result.save()

    sorted_scores = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
    return JsonResponse({
        'success': True,
        'result_id': result.id,
        'top_category': top_name,
        'top_icon': top_cat.icon if top_cat else '🌟',
        'top_color': top_cat.color if top_cat else '#667eea',
        'description': top_cat.description if top_cat else '',
        'careers': top_cat.get_career_suggestions() if top_cat else [],
        'sorted_scores': sorted_scores,
    })


def interests_result(request, result_id):
    """Natija sahifasi"""
    result = get_object_or_404(InterestResult, id=result_id)
    scores = result.get_scores()
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    categories_map = {c.name: c for c in InterestCategory.objects.all()}
    return render(request, 'exams/edukids/interests/result.html', {
        'result': result,
        'sorted_scores': sorted_scores,
        'categories_map': categories_map,
    })


# ============ MANTIQIY FIKRLASH (9-14 YOŠ) ============

def logic_home(request):
    """Mantiqiy fikrlash bosh sahifasi"""
    exercises = LogicExercise.objects.filter(is_active=True)
    exercise_types = LogicExercise.EXERCISE_TYPES
    difficulty_counts = {
        1: exercises.filter(difficulty=1).count(),
        2: exercises.filter(difficulty=2).count(),
        3: exercises.filter(difficulty=3).count(),
    }
    user_results = {}
    if request.user.is_authenticated:
        for r in LogicResult.objects.filter(user=request.user):
            if r.exercise_id not in user_results or r.score > user_results[r.exercise_id]['score']:
                user_results[r.exercise_id] = {'score': r.score, 'total': r.total_questions, 'pct': r.percentage()}
    return render(request, 'exams/edukids/logic/home.html', {
        'exercises': exercises,
        'exercise_types': exercise_types,
        'difficulty_counts': difficulty_counts,
        'user_results': user_results,
    })


def logic_exercise_play(request, exercise_id):
    """Mantiqiy mashqni bajarish"""
    exercise = get_object_or_404(LogicExercise, id=exercise_id, is_active=True)
    questions = list(exercise.logic_questions.all())
    questions_data = []
    for q in questions:
        questions_data.append({
            'id': q.id,
            'text': q.question_text,
            'options': q.get_options(),
            'correct': q.correct_answer,
            'hint': q.hint,
            'explanation': q.explanation,
            'points': q.points,
        })
    return render(request, 'exams/edukids/logic/play.html', {
        'exercise': exercise,
        'questions': questions,
        'questions_json': json.dumps(questions_data, ensure_ascii=False),
    })


def logic_submit(request, exercise_id):
    """Mantiqiy mashq natijasini saqlash"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST kerak'}, status=405)
    exercise = get_object_or_404(LogicExercise, id=exercise_id)
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': "Noto'g'ri so'rov"}, status=400)

    score = int(data.get('score', 0))
    total = int(data.get('total', 0))
    time_spent = int(data.get('time_spent', 0))

    result = LogicResult(
        exercise=exercise,
        score=score,
        total_questions=total,
        time_spent=time_spent,
    )
    if request.user.is_authenticated:
        result.user = request.user
    result.save()

    percentage = round(score / total * 100) if total > 0 else 0
    badge = ''
    if percentage == 100:
        badge = 'Mukammal! 🏆'
    elif percentage >= 80:
        badge = 'A\'lo! ⭐'
    elif percentage >= 60:
        badge = "Yaxshi! 👍"
    else:
        badge = "Davom eting! 💪"

    return JsonResponse({
        'success': True,
        'score': score,
        'total': total,
        'percentage': percentage,
        'badge': badge,
    })

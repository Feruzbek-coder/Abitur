import random, json
from typing import TYPE_CHECKING
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Question, TestAttempt, QuestionResult, UserProfile, Subject

if TYPE_CHECKING:
    from django.db.models import QuerySet


@csrf_exempt
def start_teacher_test(request, subject_id):
    """O'qituvchi attestatsiyasi uchun savol ro'yxatini qaytaradi"""
    subject = get_object_or_404(Subject, id=subject_id, is_active=True)
    pool = list(Question.objects.filter(subject=subject))
    if not pool:
        return JsonResponse({'error': 'Bu fan bo\'yicha savollar mavjud emas'}, status=400)
    count = min(len(pool), 30)
    selected = random.sample(pool, count)
    questions_data = []
    for q in selected:
        questions_data.append({
            'id': str(q.id),
            'text': q.text,
            'correct': q.correct,
            'options': {
                'A': q.option_a,
                'B': q.option_b,
                'C': q.option_c or '',
                'D': q.option_d or '',
            }
        })
    return JsonResponse({'questions': questions_data})

def start_test(request, level):
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"start_test called with level: {level}")
    
    from django.contrib.auth import get_user_model
    from .models import UserProfile
    User = get_user_model()
    
    user = request.user
    # Test uchun authentication ni vaqtincha o'chiramiz
    if not user.is_authenticated:
        # Anonymous user uchun test user yaratamiz yoki olamiz
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com'}
        )

    # Foydalanuvchi profiliga qarab savollar tanlaymiz
    try:
        profile = UserProfile.objects.get(user=user)
        if profile.selected_subject:
            # Yo'nalish bo'yicha savollar
            pool = list(Question.objects.filter(subject=profile.selected_subject))
        else:
            # Standart savollar
            pool = list(Question.objects.filter(level=level))
    except UserProfile.DoesNotExist:
        # Profil yo'q bo'lsa standart savollar
        pool = list(Question.objects.filter(level=level))
    if len(pool) < 1:
        return JsonResponse({'error': 'Savollar yetarli emas'}, status=400)

    # Mavjud savollar soniga qarab tanlaymiz
    select_count = min(len(pool), 5)  # Test uchun 5 ta savol
    selected = random.sample(pool, select_count)
    attempt = TestAttempt.objects.create(user=user, level=level, max_score=select_count)

    # Savollarni TestAttempt bilan bog‘lash
    for q in selected:
        QuestionResult.objects.create(attempt=attempt, question=q)

    first = selected[0]
    return JsonResponse({
        'attempt_id': str(attempt.id),
        'question_id': str(first.id),
        'text': first.text,
        'options': {
            'A': first.option_a,
            'B': first.option_b,
            'C': first.option_c,
            'D': first.option_d,
        },
        'time_per_question': 10
    })

@csrf_exempt
def submit_answer(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST yuboring"}, status=405)

    data = json.loads(request.body)
    attempt = get_object_or_404(TestAttempt, id=data['attempt_id'], user=request.user)
    qres = get_object_or_404(QuestionResult, question_id=data['question_id'], attempt=attempt)

    chosen = data['chosen']
    qres.chosen = chosen
    qres.time_taken = data.get('time_taken', 0)
    qres.correct = (chosen == qres.question.correct)
    qres.save()

    if qres.correct:
        attempt.score += 1
    else:
        attempt.score -= 1
    attempt.save()

    remaining = attempt.results.filter(chosen__isnull=True)  # type: ignore
    if remaining.exists():
        next_q = remaining.first().question
        return JsonResponse({
            'question_id': str(next_q.id),
            'text': next_q.text,
            'options': {
                'A': next_q.option_a,
                'B': next_q.option_b,
                'C': next_q.option_c,
                'D': next_q.option_d,
            }
        })
    else:
        attempt.finished_at = timezone.now()
        attempt.save()
        return JsonResponse({'finished': True, 'score': attempt.score})

def results_view(request):
    """Foydalanuvchining test natijalarini ko'rsatish"""
    from django.shortcuts import render
    from django.contrib.auth.decorators import login_required
    
    @login_required
    def inner_view(request):
        # Foydalanuvchining barcha test urinishlarini olish
        attempts = TestAttempt.objects.filter(
            user=request.user
        ).select_related('user').prefetch_related('results__question').order_by('-started_at')
        
        # Har bir urinish uchun batafsil ma'lumot
        attempts_data = []
        for attempt in attempts:
            total_questions = attempt.results.count()
            correct_answers = attempt.results.filter(correct=True).count()
            wrong_answers = attempt.results.filter(correct=False).count()
            unanswered = attempt.results.filter(chosen__isnull=True).count()
            
            # Foiz hisobini chiqarish
            percentage = (correct_answers / total_questions * 100) if total_questions > 0 else 0
            
            attempts_data.append({
                'attempt': attempt,
                'total_questions': total_questions,
                'correct_answers': correct_answers,
                'wrong_answers': wrong_answers,
                'unanswered': unanswered,
                'percentage': round(percentage, 1),
                'is_finished': attempt.finished_at is not None,
            })
        
        context = {
            'attempts_data': attempts_data,
            'total_attempts': attempts.count(),
        }
        
        return render(request, 'exams/results.html', context)
    
    return inner_view(request)

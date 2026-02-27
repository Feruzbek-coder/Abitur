from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from exams.models import Question, TestAttempt, QuestionResult


class Command(BaseCommand):
    help = 'Tizim statistikasini ko\'rsatadi'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('📊 Abitur Test Tizim Statistikasi'))
        self.stdout.write('=' * 50)
        
        # Foydalanuvchilar
        users_count = User.objects.count()
        self.stdout.write(f'👥 Foydalanuvchilar: {users_count}')
        
        # Savollar
        questions_count = Question.objects.count()
        self.stdout.write(f'❓ Savollar: {questions_count}')
        
        # Testlar
        tests_count = TestAttempt.objects.count()
        completed_tests = TestAttempt.objects.filter(finished_at__isnull=False).count()
        self.stdout.write(f'📝 Jami testlar: {tests_count}')
        self.stdout.write(f'✅ Yakunlangan testlar: {completed_tests}')
        
        # Javoblar
        answers_count = QuestionResult.objects.count()
        correct_answers = QuestionResult.objects.filter(correct=True).count()
        if answers_count > 0:
            accuracy = (correct_answers / answers_count) * 100
            self.stdout.write(f'📊 Jami javoblar: {answers_count}')
            self.stdout.write(f'✅ To\'g\'ri javoblar: {correct_answers}')
            self.stdout.write(f'📈 Umumiy aniqlik: {accuracy:.2f}%')
        
        # Level bo'yicha statistika
        self.stdout.write('\n📊 Level bo\'yicha savollar:')
        for level in [1, 2, 3]:
            count = Question.objects.filter(level=level).count()
            self.stdout.write(f'  Level {level}: {count} ta savol')
        
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS('✅ Statistika tayyor!'))
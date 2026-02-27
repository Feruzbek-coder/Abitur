from django.core.management.base import BaseCommand
from exams.models import Subject


class Command(BaseCommand):
    help = 'Asosiy yo\'nalishlarni yaratadi'

    def handle(self, *args, **options):
        subjects_data = [
            {
                'name': 'physics_math',
                'display_name': 'Fizika-Matematika',
                'description': 'Fizika va Matematika fanlaridan savollar'
            },
            {
                'name': 'biology_chemistry', 
                'display_name': 'Biologiya-Kimyo',
                'description': 'Biologiya va Kimyo fanlaridan savollar'
            },
            {
                'name': 'languages',
                'display_name': 'Tillar',
                'description': 'Ingliz tili va boshqa tillardan savollar'
            },
            {
                'name': 'social_studies',
                'display_name': 'Ijtimoiy fanlar', 
                'description': 'Tarix, Geografiya va ijtimoiy fanlardan savollar'
            }
        ]
        
        for data in subjects_data:
            subject, created = Subject.objects.get_or_create(
                name=data['name'],
                defaults={
                    'display_name': data['display_name'],
                    'description': data['description'],
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Yaratildi: {subject.display_name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Mavjud: {subject.display_name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS('🎉 Barcha yo\'nalishlar tayyor!')
        )
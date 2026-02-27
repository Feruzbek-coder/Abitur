from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from exams.models import UserProfile


class Command(BaseCommand):
    help = 'Barcha foydalanuvchilar uchun profil yaratadi'

    def handle(self, *args, **options):
        users_without_profile = []
        
        for user in User.objects.all():
            if not hasattr(user, 'profile'):
                UserProfile.objects.create(user=user)
                users_without_profile.append(user.username)
                self.stdout.write(
                    self.style.SUCCESS(f'✅ {user.username} uchun profil yaratildi')
                )
        
        if not users_without_profile:
            self.stdout.write(
                self.style.WARNING('⚠️  Barcha foydalanuvchilar profiliga ega')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'🎉 {len(users_without_profile)} ta profil yaratildi!')
            )
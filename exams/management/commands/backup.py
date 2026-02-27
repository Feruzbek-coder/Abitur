from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
import os
import shutil
from datetime import datetime


class Command(BaseCommand):
    help = 'Tizimni backup qiladi'

    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            type=str,
            default='backups',
            help='Backup saqlash joyi'
        )

    def handle(self, *args, **options):
        backup_path = options['path']
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Backup papkasini yaratish
        if not os.path.exists(backup_path):
            os.makedirs(backup_path)
        
        self.stdout.write(self.style.SUCCESS(f'🔄 Backup boshlanmoqda... ({timestamp})'))
        
        # Database backup
        db_backup_file = os.path.join(backup_path, f'db_backup_{timestamp}.json')
        try:
            call_command('dumpdata', output=db_backup_file, indent=2)
            self.stdout.write(self.style.SUCCESS(f'✅ Database backup: {db_backup_file}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Database backup xatolik: {e}'))
        
        # Media fayllar backup (agar mavjud bo'lsa)
        if hasattr(settings, 'MEDIA_ROOT') and os.path.exists(settings.MEDIA_ROOT):
            media_backup = os.path.join(backup_path, f'media_backup_{timestamp}')
            try:
                shutil.copytree(settings.MEDIA_ROOT, media_backup)
                self.stdout.write(self.style.SUCCESS(f'✅ Media backup: {media_backup}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Media backup xatolik: {e}'))
        
        self.stdout.write(self.style.SUCCESS('✅ Backup yakunlandi!'))
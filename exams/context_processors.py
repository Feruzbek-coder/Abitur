from .models import Subject


def subjects_context(request):
    """Barcha sahifalarda fanlar ro'yxatini mavjud qiladi (navbar dropdown uchun)"""
    return {
        'nav_subjects': Subject.objects.filter(is_active=True)
    }

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponse
from .models import Subject, UserProfile, Question
from .forms import CustomUserCreationForm, ProfileForm


def universities_view(request):
    """Oliy o'quv yurtlari sahifasi"""
    context = {
        'title': 'Oliygohlar',
        'page_title': 'Oliygohlar',
        'description': 'O\'zbekistondagi oliy o\'quv yurtlari haqida ma\'lumotlar. Tez orada bu sahifada barcha oliygohlar ro\'yxati va ular haqida batafsil ma\'lumot joylashtiriladi.'
    }
    return render(request, 'exams/info_page.html', context)


def admission_2026_view(request):
    """Qabul 2026 sahifasi"""
    context = {
        'title': 'Qabul 2026',
        'page_title': 'Qabul 2026',
        'description': '2026-yilgi oliy o\'quv yurtlariga qabul haqida ma\'lumotlar. Qabul jarayoni, muhim sanalar, talablar va boshqa foydali ma\'lumotlar tez orada bu yerda joylanadi.'
    }
    return render(request, 'exams/info_page.html', context)


def abiturient_center_view(request):
    """Abituriyent Shtabi sahifasi"""
    context = {
        'title': 'Abituriyent Shtabi',
        'page_title': 'Abituriyent Shtabi',
        'description': 'Abituriyentlar uchun yordam markazi. Bu yerda siz o\'quv markazlari, kurslar, maslahatlar va abituriyentlar uchun foydali resurslarni topasiz. Ma\'lumotlar tez orada yangilanadi.'
    }
    return render(request, 'exams/info_page.html', context)


def home_view(request):
    """Bosh sahifa - login/register tugmalari va yo'nalish tanlash"""
    if request.user.is_authenticated:
        # Agar foydalanuvchi login bo'lgan bo'lsa, profil sahifasiga yo'naltirish
        return redirect('exams:dashboard')
    
    subjects = Subject.objects.filter(is_active=True)
    context = {
        'subjects': subjects,
        'title': 'Abitur Test Tizimi'
    }
    return render(request, 'exams/home.html', context)


def register_view(request):
    """Ro'yxatdan o'tish"""
    if request.user.is_authenticated:
        return redirect('exams:dashboard')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'{username}, muvaffaqiyatli ro\'yxatdan o\'tdingiz!')
            
            # Avtomatik login qilish
            user = authenticate(username=username, password=form.cleaned_data.get('password1'))
            if user:
                login(request, user)
                return redirect('exams:profile_setup')
    else:
        form = CustomUserCreationForm()
    
    context = {
        'form': form,
        'title': 'Ro\'yxatdan o\'tish'
    }
    return render(request, 'exams/register.html', context)


def login_view(request):
    """Kirish"""
    if request.user.is_authenticated:
        return redirect('exams:dashboard')
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Muvaffaqiyatli kirdingiz!')
            next_url = request.GET.get('next', 'exams:dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Noto\'g\'ri username yoki parol!')
    
    context = {
        'title': 'Kirish'
    }
    return render(request, 'exams/login.html', context)


@login_required
def logout_view(request):
    """Chiqish"""
    logout(request)
    messages.info(request, 'Tizimdan chiqdingiz.')
    return redirect('exams:home')


@login_required
def profile_setup_view(request):
    """Profil sozlash - yo'nalish tanlash"""
    # Profil mavjudligini tekshirish
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil muvaffaqiyatli yangilandi!')
            return redirect('exams:dashboard')
    else:
        form = ProfileForm(instance=profile)
    
    context = {
        'form': form,
        'title': 'Profil sozlash',
        'user': request.user
    }
    return render(request, 'exams/profile_setup.html', context)


@login_required
def dashboard_view(request):
    """Asosiy dashboard - testlar sahifasi"""
    # Profil mavjudligini tekshirish
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        # Agar profil yo'q bo'lsa, yaratamiz
        profile = UserProfile.objects.create(user=request.user)
        messages.info(request, 'Profil yaratildi. Iltimos, yo\'nalishni tanlang.')
        return redirect('exams:profile_setup')
    
    if not profile.selected_subject:
        messages.warning(request, 'Iltimos, avval yo\'nalishni tanlang.')
        return redirect('exams:profile_setup')
    
    context = {
        'title': 'Bosh sahifa',
        'user': request.user,
        'profile': profile,
    }
    return render(request, 'exams/dashboard.html', context)


@login_required  
def profile_view(request):
    """Profil ko'rish va tahrirlash"""
    # Profil mavjudligini tekshirish
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil yangilandi!')
            return redirect('exams:profile')
    else:
        form = ProfileForm(instance=profile)
    
    context = {
        'form': form,
        'title': 'Mening profilim',
        'user': request.user,
        'profile': profile
    }
    return render(request, 'exams/profile.html', context)


def teacher_attestation_view(request):
    """O'qituvchilar attestatsiyasi - fanlar ro'yxati"""
    subjects = Subject.objects.filter(is_active=True)
    context = {
        'subjects': subjects,
        'title': "O'qituvchilar Attestatsiyasi"
    }
    return render(request, 'exams/teacher_attestation.html', context)


def teacher_test_view(request, subject_id):
    """O'qituvchi uchun tanlangan fan bo'yicha test sahifasi"""
    subject = get_object_or_404(Subject, id=subject_id, is_active=True)
    questions_count = Question.objects.filter(subject=subject).count()
    test_count = min(questions_count, 30)

    if questions_count == 0:
        messages.error(request, f'{subject.display_name} bo\'yicha savollar mavjud emas.')
        return redirect('exams:teacher_attestation')

    context = {
        'subject': subject,
        'test_count': test_count,
        'questions_count': questions_count,
        'title': f"Attestatsiya - {subject.display_name}",
    }
    return render(request, 'exams/teacher_test.html', context)


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.db.models import Q, Count
from .models import School, SchoolManager, SchoolMembership, SchoolTest, Question
from django.template.loader import render_to_string


@login_required
def my_school_view(request):
    """Mening maktabim sahifasi"""
    # Foydalanuvchi qaysi maktablarga a'zo
    memberships = SchoolMembership.objects.filter(
        user=request.user,
        is_active=True
    ).select_related('school')
    
    # Foydalanuvchi boshqaradigan maktablar
    managed_schools = SchoolManager.objects.filter(
        user=request.user,
        is_active=True
    ).select_related('school')
    
    # Foydalanuvchi a'zo bo'lgan yoki boshqaradigan maktablar ID-lari
    member_school_ids = list(memberships.values_list('school_id', flat=True))
    managed_school_ids = list(managed_schools.values_list('school_id', flat=True))
    joined_school_ids = member_school_ids + managed_school_ids
    
    # Barcha maktablar ro'yxati (qo'shilish uchun)
    all_schools = School.objects.filter(is_active=True).order_by('region', 'name')
    
    context = {
        'memberships': memberships,
        'managed_schools': managed_schools,
        'all_schools': all_schools,
        'joined_school_ids': joined_school_ids,
        'title': 'Mening Maktabim'
    }
    return render(request, 'exams/my_school.html', context)


@login_required
def create_school_view(request):
    """Maktab yaratish"""
    if request.method == 'POST':
        name = request.POST.get('name')
        region = request.POST.get('region')
        district = request.POST.get('district', '')
        school_number = request.POST.get('school_number', '')
        address = request.POST.get('address', '')
        description = request.POST.get('description', '')
        
        # Maktab yaratish
        school = School.objects.create(
            name=name,
            region=region,
            district=district,
            school_number=school_number,
            address=address,
            description=description
        )
        
        # Yaratuvchini boshqaruvchi qilish
        SchoolManager.objects.create(
            school=school,
            user=request.user,
            role='founder',
            can_manage_members=True,
            can_create_tests=True,
            can_print_tests=True
        )
        
        messages.success(request, f'"{school.name}" maktabi muvaffaqiyatli yaratildi!')
        return redirect('exams:my_school')
    
    return render(request, 'exams/create_school.html', {'title': 'Maktab Yaratish'})


@login_required
def join_school_view(request, school_id):
    """Maktabga qo'shilish so'rovi yuborish"""
    school = get_object_or_404(School, id=school_id, is_active=True)
    
    # Allaqachon a'zo yoki so'rov yuborilganmi tekshirish
    existing = SchoolMembership.objects.filter(
        school=school,
        user=request.user,
        is_active=True
    ).first()
    
    if existing:
        if existing.status == 'pending':
            messages.warning(request, 'Sizning so\'rovingiz hali ko\'rib chiqilmoqda.')
        elif existing.status == 'approved':
            messages.info(request, 'Siz allaqachon bu maktab a\'zosisiz.')
        elif existing.status == 'rejected':
            messages.error(request, 'Sizning so\'rovingiz rad etilgan.')
        return redirect('exams:my_school')
    
    if request.method == 'POST':
        message = request.POST.get('message', '')
        
        SchoolMembership.objects.create(
            school=school,
            user=request.user,
            message=message,
            status='pending'
        )
        
        messages.success(request, f'"{school.name}" maktabiga qo\'shilish so\'rovi yuborildi!')
        return redirect('exams:my_school')
    
    context = {
        'school': school,
        'title': f'{school.name}ga qo\'shilish'
    }
    return render(request, 'exams/join_school.html', context)


@login_required
def school_dashboard_view(request, school_id):
    """Maktab boshqaruv paneli"""
    school = get_object_or_404(School, id=school_id)
    
    # Boshqaruvchi ekanligini tekshirish
    manager = SchoolManager.objects.filter(
        school=school,
        user=request.user,
        is_active=True
    ).first()
    
    if not manager:
        messages.error(request, 'Sizda bu maktabni boshqarish huquqi yo\'q.')
        return redirect('exams:my_school')
    
    # Statistika
    pending_requests = school.get_pending_requests()
    approved_members = school.get_members()
    school_tests = SchoolTest.objects.filter(school=school).order_by('-created_at')
    
    context = {
        'school': school,
        'manager': manager,
        'pending_requests': pending_requests,
        'approved_members': approved_members,
        'school_tests': school_tests,
        'title': f'{school.name} - Boshqaruv'
    }
    return render(request, 'exams/school_dashboard.html', context)


@login_required
def approve_membership_view(request, membership_id):
    """So'rovni tasdiqlash"""
    membership = get_object_or_404(SchoolMembership, id=membership_id)
    
    # Boshqaruvchi ekanligini tekshirish
    manager = SchoolManager.objects.filter(
        school=membership.school,
        user=request.user,
        is_active=True,
        can_manage_members=True
    ).first()
    
    if not manager:
        messages.error(request, 'Sizda bu amalni bajarish huquqi yo\'q.')
        return redirect('exams:my_school')
    
    if membership.status == 'pending':
        membership.approve(request.user)
        messages.success(request, f'{membership.user.username} maktabga qo\'shildi!')
    
    return redirect('exams:school_dashboard', school_id=membership.school.id)


@login_required
def reject_membership_view(request, membership_id):
    """So'rovni rad etish"""
    membership = get_object_or_404(SchoolMembership, id=membership_id)
    
    # Boshqaruvchi ekanligini tekshirish
    manager = SchoolManager.objects.filter(
        school=membership.school,
        user=request.user,
        is_active=True,
        can_manage_members=True
    ).first()
    
    if not manager:
        messages.error(request, 'Sizda bu amalni bajarish huquqi yo\'q.')
        return redirect('exams:my_school')
    
    if membership.status == 'pending':
        membership.reject(request.user)
        messages.info(request, f'{membership.user.username}ning so\'rovi rad etildi.')
    
    return redirect('exams:school_dashboard', school_id=membership.school.id)


@login_required
def create_school_test_view(request, school_id):
    """Maktab uchun test yaratish"""
    school = get_object_or_404(School, id=school_id)
    
    # Boshqaruvchi ekanligini tekshirish
    manager = SchoolManager.objects.filter(
        school=school,
        user=request.user,
        is_active=True,
        can_create_tests=True
    ).first()
    
    if not manager:
        messages.error(request, 'Sizda test yaratish huquqi yo\'q.')
        return redirect('exams:my_school')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        level = int(request.POST.get('level', 1))
        duration = int(request.POST.get('duration', 60))
        max_attempts = int(request.POST.get('max_attempts', 1))
        question_ids = request.POST.getlist('questions')
        
        # Test yaratish
        test = SchoolTest.objects.create(
            school=school,
            created_by=request.user,
            title=title,
            description=description,
            level=level,
            duration_minutes=duration,
            max_attempts=max_attempts
        )
        
        # Savollarni qo'shish
        if question_ids:
            test.questions.set(question_ids)
        
        messages.success(request, f'"{title}" testi yaratildi!')
        return redirect('exams:school_dashboard', school_id=school.id)
    
    # Mavjud savollar
    questions = Question.objects.all().order_by('subject', 'level')
    
    context = {
        'school': school,
        'questions': questions,
        'title': 'Yangi Test Yaratish'
    }
    return render(request, 'exams/create_school_test.html', context)


@login_required
def print_test_view(request, test_id):
    """Testni chop etish uchun sahifa"""
    test = get_object_or_404(SchoolTest, id=test_id)
    
    # Boshqaruvchi ekanligini tekshirish
    manager = SchoolManager.objects.filter(
        school=test.school,
        user=request.user,
        is_active=True,
        can_print_tests=True
    ).first()
    
    if not manager:
        messages.error(request, 'Sizda test chop etish huquqi yo\'q.')
        return redirect('exams:my_school')
    
    # Testdagi savollar
    questions = test.questions.all().order_by('level', 'id')
    
    context = {
        'test': test,
        'questions': questions,
        'school': test.school,
        'title': f'{test.title} - Chop etish'
    }
    return render(request, 'exams/print_test.html', context)


@login_required
def school_members_view(request, school_id):
    """Maktab o'quvchilari ro'yxati"""
    school = get_object_or_404(School, id=school_id)
    
    # Boshqaruvchi yoki a'zo ekanligini tekshirish
    is_manager = SchoolManager.objects.filter(
        school=school,
        user=request.user,
        is_active=True
    ).exists()
    
    is_member = SchoolMembership.objects.filter(
        school=school,
        user=request.user,
        status='approved',
        is_active=True
    ).exists()
    
    if not (is_manager or is_member):
        messages.error(request, 'Sizda bu sahifani ko\'rish huquqi yo\'q.')
        return redirect('exams:my_school')
    
    members = school.get_members()
    
    context = {
        'school': school,
        'members': members,
        'is_manager': is_manager,
        'title': f'{school.name} - O\'quvchilar'
    }
    return render(request, 'exams/school_members.html', context)

from django.urls import path
from . import views
from . import test_views
from . import simple_test
from . import auth_views
from . import school_views
from . import news_views

app_name = 'exams'

urlpatterns = [
    # API endpoints
    path('api/start/<int:level>/', views.start_test, name='start_test'),
    path('api/submit/', views.submit_answer, name='submit_answer'),
    path('api/questions/', test_views.questions_list, name='questions_list'),
    path('api/teacher-start/<int:subject_id>/', views.start_teacher_test, name='start_teacher_test'),
    
    # Test sahifalari
    path('test/', test_views.test_page, name='test_page'),
    path('simple/', simple_test.simple_test_page, name='simple_test'),
    
    # Authentication
    path('', auth_views.home_view, name='home'),
    path('login/', auth_views.login_view, name='login'),
    path('register/', auth_views.register_view, name='register'),
    path('logout/', auth_views.logout_view, name='logout'),
    
    # Info pages
    path('universities/', auth_views.universities_view, name='universities'),
    path('admission-2026/', auth_views.admission_2026_view, name='admission_2026'),
    path('abiturient-center/', auth_views.abiturient_center_view, name='abiturient_center'),
    
    # Teacher attestation
    path('teacher-attestation/', auth_views.teacher_attestation_view, name='teacher_attestation'),
    path('teacher-attestation/<int:subject_id>/', auth_views.teacher_test_view, name='teacher_test'),
    
    # News
    path('news/', news_views.news_list_view, name='news_list'),
    path('news/<slug:slug>/', news_views.news_detail_view, name='news_detail'),
    
    # User pages  
    path('dashboard/', auth_views.dashboard_view, name='dashboard'),
    path('profile/', auth_views.profile_view, name='profile'),
    path('profile/setup/', auth_views.profile_setup_view, name='profile_setup'),
    path('results/', views.results_view, name='results'),
    
    # School pages
    path('my-school/', school_views.my_school_view, name='my_school'),
    path('school/create/', school_views.create_school_view, name='create_school'),
    path('school/<int:school_id>/join/', school_views.join_school_view, name='join_school'),
    path('school/<int:school_id>/dashboard/', school_views.school_dashboard_view, name='school_dashboard'),
    path('school/<int:school_id>/members/', school_views.school_members_view, name='school_members'),
    path('school/membership/<int:membership_id>/approve/', school_views.approve_membership_view, name='approve_membership'),
    path('school/membership/<int:membership_id>/reject/', school_views.reject_membership_view, name='reject_membership'),
    path('school/<int:school_id>/test/create/', school_views.create_school_test_view, name='create_school_test'),
    path('school/test/<int:test_id>/print/', school_views.print_test_view, name='print_test'),
]
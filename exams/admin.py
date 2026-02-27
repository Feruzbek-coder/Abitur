from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Question, TestAttempt, QuestionResult, UserProfile, Subject

# Admin panel sarlavhalarini o'zgartirish
admin.site.site_header = "Abitur Test Boshqaruv Paneli"
admin.site.site_title = "Abitur Test Admin"
admin.site.index_title = "Abitur Test tizimini boshqarish"

# Subject modelini admin panelga qo'shish
@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'name', 'is_active', 'question_count')
    list_filter = ('is_active', 'name')
    search_fields = ('display_name', 'description')
    list_editable = ('is_active',)
    
    def question_count(self, obj):
        return obj.questions.count()
    question_count.short_description = 'Savollar soni'

# UserProfile inline
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profil'
    fk_name = 'user'
    fields = ('selected_subject', 'phone_number', 'birth_date', 'school')

# User modelini yangilash
class CustomUserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'get_subject')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'profile__selected_subject')
    
    def get_subject(self, obj):
        if hasattr(obj, 'profile') and obj.profile.selected_subject:
            return obj.profile.selected_subject.display_name
        return "Tanlanmagan"
    get_subject.short_description = 'Yo\'nalish'

# User modelini qayta ro'yxatdan o'tkazish
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# UserProfile ni alohida admin sifatida ham qo'shish
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'selected_subject', 'phone_number', 'school', 'created_at')
    list_filter = ('selected_subject', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone_number', 'school')
    raw_id_fields = ('user',)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text_preview', 'subject', 'level', 'correct', 'created_at')
    list_filter = ('subject', 'level', 'created_at')
    search_fields = ('text', 'option_a', 'option_b', 'option_c', 'option_d')
    list_per_page = 20
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Savol Ma\'lumotlari', {
            'fields': ('subject', 'text', 'level')
        }),
        ('Javob Variantlari', {
            'fields': ('option_a', 'option_b', 'option_c', 'option_d')
        }),
        ('To\'g\'ri Javob', {
            'fields': ('correct',)
        }),
    )
    
    def text_preview(self, obj):
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Savol matni'

@admin.register(TestAttempt)
class TestAttemptAdmin(admin.ModelAdmin):
    list_display = ('id_short', 'user_display', 'level', 'score', 'max_score', 'started_at', 'is_finished')
    list_filter = ('level', 'started_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('id', 'started_at', 'finished_at')
    list_per_page = 25
    ordering = ('-started_at',)
    
    def id_short(self, obj):
        return str(obj.id)[:8] + "..."
    id_short.short_description = 'ID'
    
    def user_display(self, obj):
        return obj.user.username if obj.user else "Anonim"
    user_display.short_description = 'Foydalanuvchi'
    
    def is_finished(self, obj):
        return "✅ Ha" if obj.finished_at else "❌ Yo'q"
    is_finished.short_description = 'Yakunlandi'

class QuestionResultInline(admin.TabularInline):
    model = QuestionResult
    extra = 0
    readonly_fields = ('question', 'chosen', 'correct', 'time_taken')

@admin.register(QuestionResult)
class QuestionResultAdmin(admin.ModelAdmin):
    list_display = ('attempt_short', 'question_preview', 'chosen', 'correct', 'time_taken')
    list_filter = ('correct', 'chosen')
    search_fields = ('attempt__user__username', 'question__text')
    readonly_fields = ('attempt', 'question', 'chosen', 'correct', 'time_taken')
    list_per_page = 30
    ordering = ('-attempt__started_at',)
    
    def attempt_short(self, obj):
        return str(obj.attempt.id)[:8] + "..."
    attempt_short.short_description = 'Test'
    
    def question_preview(self, obj):
        return obj.question.text[:50] + "..." if len(obj.question.text) > 50 else obj.question.text
    question_preview.short_description = 'Savol'

# TestAttempt ga inline qo'shish
TestAttemptAdmin.inlines = [QuestionResultInline]

# Maktab modellari uchun admin
from .models import School, SchoolManager, SchoolMembership, SchoolTest, NewsCategory, News

@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'region', 'district', 'school_number', 'managers_count', 'members_count', 'is_active', 'created_at')
    list_filter = ('region', 'is_active', 'created_at')
    search_fields = ('name', 'region', 'district', 'school_number', 'address')
    list_editable = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    
    fieldsets = (
        ('Asosiy Ma\'lumotlar', {
            'fields': ('name', 'school_number', 'region', 'district')
        }),
        ('Qo\'shimcha', {
            'fields': ('address', 'description', 'is_active')
        }),
        ('Vaqt', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def managers_count(self, obj):
        return obj.managers.filter(is_active=True).count()
    managers_count.short_description = 'Boshqaruvchilar'
    
    def members_count(self, obj):
        return obj.memberships.filter(status='approved', is_active=True).count()
    members_count.short_description = 'O\'quvchilar'

@admin.register(SchoolManager)
class SchoolManagerAdmin(admin.ModelAdmin):
    list_display = ('user', 'school', 'role', 'can_manage_members', 'can_create_tests', 'can_print_tests', 'is_active', 'created_at')
    list_filter = ('school', 'is_active', 'can_manage_members', 'can_create_tests', 'can_print_tests')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'school__name')
    list_editable = ('is_active',)
    raw_id_fields = ('user', 'school')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Asosiy', {
            'fields': ('school', 'user', 'role')
        }),
        ('Ruxsatlar', {
            'fields': ('can_manage_members', 'can_create_tests', 'can_print_tests', 'is_active')
        }),
        ('Vaqt', {
            'fields': ('created_at',)
        }),
    )

@admin.register(SchoolMembership)
class SchoolMembershipAdmin(admin.ModelAdmin):
    list_display = ('user_display', 'school', 'status', 'requested_at', 'responded_by', 'responded_at')
    list_filter = ('status', 'school', 'is_active', 'requested_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'school__name')
    raw_id_fields = ('user', 'school', 'responded_by')
    readonly_fields = ('requested_at', 'responded_at')
    list_per_page = 30
    
    fieldsets = (
        ('So\'rov', {
            'fields': ('school', 'user', 'message', 'status')
        }),
        ('Javob', {
            'fields': ('responded_by', 'responded_at')
        }),
        ('Holat', {
            'fields': ('is_active', 'requested_at')
        }),
    )
    
    def user_display(self, obj):
        return obj.user.get_full_name() or obj.user.username
    user_display.short_description = 'Foydalanuvchi'
    
    actions = ['approve_requests', 'reject_requests']
    
    def approve_requests(self, request, queryset):
        count = 0
        for membership in queryset.filter(status='pending'):
            membership.approve(request.user)
            count += 1
        self.message_user(request, f'{count} ta so\'rov tasdiqlandi.')
    approve_requests.short_description = 'Tanlangan so\'rovlarni tasdiqlash'
    
    def reject_requests(self, request, queryset):
        count = 0
        for membership in queryset.filter(status='pending'):
            membership.reject(request.user)
            count += 1
        self.message_user(request, f'{count} ta so\'rov rad etildi.')
    reject_requests.short_description = 'Tanlangan so\'rovlarni rad etish'

@admin.register(SchoolTest)
class SchoolTestAdmin(admin.ModelAdmin):
    list_display = ('title', 'school', 'created_by', 'subject', 'level', 'duration_minutes', 'questions_count', 'is_active', 'created_at')
    list_filter = ('school', 'subject', 'level', 'is_active', 'created_at')
    search_fields = ('title', 'description', 'school__name', 'created_by__username')
    filter_horizontal = ('questions',)
    raw_id_fields = ('school', 'created_by', 'subject')
    readonly_fields = ('created_at',)
    list_per_page = 25
    
    fieldsets = (
        ('Asosiy Ma\'lumotlar', {
            'fields': ('school', 'created_by', 'title', 'description')
        }),
        ('Test Parametrlari', {
            'fields': ('subject', 'level', 'duration_minutes', 'max_attempts')
        }),
        ('Savollar', {
            'fields': ('questions',)
        }),
        ('Sana va Holat', {
            'fields': ('start_date', 'end_date', 'is_active', 'created_at')
        }),
    )
    
    def questions_count(self, obj):
        return obj.questions.count()
    questions_count.short_description = 'Savollar soni'

# Yangiliklar uchun admin
@admin.register(NewsCategory)
class NewsCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order', 'is_active', 'news_count')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('order', 'is_active')
    
    def news_count(self, obj):
        return obj.news.filter(is_published=True).count()
    news_count.short_description = 'Yangiliklar soni'

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'is_published', 'is_featured', 'views_count', 'published_at', 'created_at')
    list_filter = ('is_published', 'is_featured', 'category', 'created_at')
    search_fields = ('title', 'content', 'excerpt')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_published', 'is_featured')
    raw_id_fields = ('author',)
    readonly_fields = ('views_count', 'created_at', 'updated_at', 'published_at')
    date_hierarchy = 'published_at'
    list_per_page = 25
    
    fieldsets = (
        ('Asosiy Ma\'lumotlar', {
            'fields': ('title', 'slug', 'category', 'author')
        }),
        ('Mazmun', {
            'fields': ('excerpt', 'content', 'image')
        }),
        ('Nashr', {
            'fields': ('is_published', 'is_featured', 'published_at')
        }),
        ('Statistika', {
            'fields': ('views_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user
        super().save_model(request, obj, form, change)

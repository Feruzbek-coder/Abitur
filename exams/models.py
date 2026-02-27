from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid

User = get_user_model()

class Subject(models.Model):
    """Test yo'nalishlari"""
    SUBJECT_CHOICES = [
        ('physics_math', 'Fizika-Matematika'),
        ('biology_chemistry', 'Biologiya-Kimyo'),
        ('languages', 'Tillar'),
        ('social_studies', 'Ijtimoiy fanlar'),
    ]
    
    name = models.CharField(max_length=50, choices=SUBJECT_CHOICES, unique=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.display_name

class UserProfile(models.Model):
    """Foydalanuvchi profili"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    selected_subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    school = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        subject_name = self.selected_subject or "Yo'nalish tanlanmagan"
        return f"{self.user.username} - {subject_name}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Foydalanuvchi yaratilganda avtomatik profil yaratish"""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Foydalanuvchi o'zgarganda profilni saqlash"""
    if hasattr(instance, 'profile'):
        instance.profile.save()

class Question(models.Model):
    LEVEL_CHOICES = [(i, f'Level {i}') for i in range(1, 9)]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='questions', null=True, blank=True)
    level = models.IntegerField(choices=LEVEL_CHOICES, default=1)
    text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255, blank=True, null=True)
    option_d = models.CharField(max_length=255, blank=True, null=True)
    correct = models.CharField(max_length=1)  # 'A','B','C','D'
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        subject_name = self.subject.display_name if self.subject else "Yo'nalish belgilanmagan"
        return f"{subject_name} - {self.text[:50]}..."

    class Meta:
        ordering = ['-created_at']

class TestAttempt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    level = models.IntegerField()
    score = models.IntegerField(default=0)
    max_score = models.IntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} - Level {self.level} ({self.score}/{self.max_score})"

class QuestionResult(models.Model):
    attempt = models.ForeignKey(TestAttempt, on_delete=models.CASCADE, related_name='results')
    question = models.ForeignKey(Question, on_delete=models.PROTECT)
    chosen = models.CharField(max_length=1, null=True, blank=True)
    correct = models.BooleanField(default=False)
    time_taken = models.FloatField(null=True, blank=True)  # seconds

class School(models.Model):
    """Maktab ma'lumotlari"""
    name = models.CharField(max_length=200, verbose_name="Maktab nomi")
    region = models.CharField(max_length=100, verbose_name="Viloyat/Shahar")
    district = models.CharField(max_length=100, blank=True, verbose_name="Tuman/Shahar")
    address = models.TextField(blank=True, verbose_name="Manzil")
    school_number = models.CharField(max_length=50, blank=True, verbose_name="Maktab raqami")
    description = models.TextField(blank=True, verbose_name="Tavsif")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    
    class Meta:
        verbose_name = "Maktab"
        verbose_name_plural = "Maktablar"
        ordering = ['region', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.region})"
    
    def get_managers(self):
        """Maktab boshqaruvchilarini olish"""
        return self.managers.filter(is_active=True)
    
    def get_members(self):
        """Tasdiqlangan a'zolarni olish"""
        return self.memberships.filter(status='approved', is_active=True)
    
    def get_pending_requests(self):
        """Kutilayotgan so'rovlarni olish"""
        return self.memberships.filter(status='pending', is_active=True)

class SchoolManager(models.Model):
    """Maktab boshqaruvchisi (o'qituvchi)"""
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='managers')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='managed_schools')
    role = models.CharField(max_length=50, default='teacher', verbose_name="Rol")
    can_manage_members = models.BooleanField(default=True, verbose_name="A'zolarni boshqarish")
    can_create_tests = models.BooleanField(default=True, verbose_name="Test yaratish")
    can_print_tests = models.BooleanField(default=True, verbose_name="Testlarni chop etish")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    
    class Meta:
        verbose_name = "Maktab boshqaruvchisi"
        verbose_name_plural = "Maktab boshqaruvchilari"
        unique_together = ['school', 'user']
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.school.name}"

class SchoolMembership(models.Model):
    """Maktab a'zoligi va so'rovlar"""
    STATUS_CHOICES = [
        ('pending', 'Kutilmoqda'),
        ('approved', 'Tasdiqlangan'),
        ('rejected', 'Rad etilgan'),
    ]
    
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='school_memberships')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    message = models.TextField(blank=True, verbose_name="Xabar")
    requested_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    responded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='school_responses')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Maktab a'zoligi"
        verbose_name_plural = "Maktab a'zoliklari"
        unique_together = ['school', 'user']
        ordering = ['-requested_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.school.name} ({self.get_status_display()})"
    
    def approve(self, manager_user):
        """So'rovni tasdiqlash"""
        self.status = 'approved'
        self.responded_by = manager_user
        self.responded_at = timezone.now()
        self.save()
    
    def reject(self, manager_user):
        """So'rovni rad etish"""
        self.status = 'rejected'
        self.responded_by = manager_user
        self.responded_at = timezone.now()
        self.save()

class SchoolTest(models.Model):
    """Maktab uchun maxsus test"""
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='school_tests')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tests')
    title = models.CharField(max_length=200, verbose_name="Test nomi")
    description = models.TextField(blank=True, verbose_name="Tavsif")
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
    level = models.IntegerField(default=1, verbose_name="Daraja")
    questions = models.ManyToManyField(Question, related_name='school_tests')
    duration_minutes = models.IntegerField(default=60, verbose_name="Davomiyligi (daqiqa)")
    max_attempts = models.IntegerField(default=1, verbose_name="Maksimal urinishlar")
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    created_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField(null=True, blank=True, verbose_name="Boshlanish sanasi")
    end_date = models.DateTimeField(null=True, blank=True, verbose_name="Tugash sanasi")
    
    class Meta:
        verbose_name = "Maktab testi"
        verbose_name_plural = "Maktab testlari"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.school.name}"
    
    def is_available(self):
        """Test mavjudligini tekshirish"""
        if not self.is_active:
            return False
        now = timezone.now()
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        return True

class NewsCategory(models.Model):
    """Yangilik kategoriyalari"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Kategoriya nomi")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="URL slug")
    description = models.TextField(blank=True, verbose_name="Tavsif")
    order = models.IntegerField(default=0, verbose_name="Tartib raqami")
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    
    class Meta:
        verbose_name = "Yangilik kategoriyasi"
        verbose_name_plural = "Yangilik kategoriyalari"
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name

class News(models.Model):
    """Yangiliklar va maqolalar"""
    title = models.CharField(max_length=200, verbose_name="Sarlavha")
    slug = models.SlugField(max_length=200, unique=True, blank=True, verbose_name="URL slug")
    category = models.ForeignKey(NewsCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='news')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Muallif")
    content = models.TextField(verbose_name="Matn")
    excerpt = models.TextField(max_length=500, blank=True, verbose_name="Qisqacha")
    image = models.URLField(blank=True, verbose_name="Rasm URL")
    views_count = models.IntegerField(default=0, verbose_name="Ko'rishlar soni")
    is_featured = models.BooleanField(default=False, verbose_name="Asosiy yangilik")
    is_published = models.BooleanField(default=False, verbose_name="Nashr qilingan")
    published_at = models.DateTimeField(null=True, blank=True, verbose_name="Nashr sanasi")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Yangilik"
        verbose_name_plural = "Yangiliklar"
        ordering = ['-published_at', '-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Slug avtomatik yaratish
        if not self.slug:
            from django.utils.text import slugify
            base_slug = slugify(self.title, allow_unicode=True)
            slug = base_slug
            counter = 1
            while News.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        
        # Nashr sanasini avtomatik belgilash
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    def increment_views(self):
        """Ko'rishlar sonini oshirish"""
        self.views_count += 1
        self.save(update_fields=['views_count'])

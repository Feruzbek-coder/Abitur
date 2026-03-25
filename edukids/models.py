import json
from django.db import models
from django.contrib.auth.models import User


# ============ VOCABULARY MODELS ============

class VocabularyCategory(models.Model):
    """Vocabulary kategoriyalari: Animals, Food, Family, etc."""
    LEVEL_CHOICES = [
        ('A1', 'A1 - Boshlang\'ich'),
        ('A2', 'A2 - Elementar'),
        ('B1', 'B1 - O\'rta'),
        ('B2', 'B2 - Yuqori o\'rta'),
    ]
    name = models.CharField(max_length=64)
    name_uz = models.CharField(max_length=64)
    description = models.TextField(blank=True, null=True)
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='A1')
    icon = models.CharField(max_length=50, default='📚')
    order = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Vocabulary Kategoriyasi'
        verbose_name_plural = 'Vocabulary Kategoriyalari'
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.icon} {self.name}"

    def word_count(self):
        return self.words.count()


class Word(models.Model):
    """So'zlar bazasi"""
    LEVEL_CHOICES = VocabularyCategory.LEVEL_CHOICES
    english = models.CharField(max_length=100, db_index=True)
    uzbek = models.CharField(max_length=100, db_index=True)
    pronunciation = models.CharField(max_length=100, blank=True, null=True)
    example_sentence = models.TextField(blank=True, null=True)
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='A1', db_index=True)
    category = models.ForeignKey(VocabularyCategory, on_delete=models.CASCADE, related_name='words')
    image_url = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = 'So\'z'
        verbose_name_plural = 'So\'zlar'

    def __str__(self):
        return f"{self.english} - {self.uzbek}"


# ============ GRAMMAR MODELS ============

class GrammarTopic(models.Model):
    """Grammar mavzulari: Present Simple, Past Simple, etc."""
    LEVEL_CHOICES = VocabularyCategory.LEVEL_CHOICES
    title = models.CharField(max_length=128)
    title_uz = models.CharField(max_length=128, blank=True, null=True)
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='A1')
    description = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)  # HTML formatida qoida
    order = models.IntegerField(default=0)
    icon = models.CharField(max_length=50, default='📖')

    class Meta:
        verbose_name = 'Grammar Mavzusi'
        verbose_name_plural = 'Grammar Mavzulari'
        ordering = ['level', 'order']

    def __str__(self):
        return f"{self.icon} {self.title}"


# ============ EXERCISE MODELS ============

class Exercise(models.Model):
    """Mashqlar - Grammar va Vocabulary uchun"""
    EXERCISE_TYPES = [
        ('multiple_choice', 'Test savollari ✅'),
        ('fill_gaps', "Bo'sh joylarni to'ldiring 📝"),
        ('matching', "So'zlarni moslashtiring 🔗"),
        ('word_search', "So'z qidirish 🔍"),
        ('word_scramble', "Harflarni joylashtiring 🔤"),
        ('crossword', 'Krossvord 📰'),
    ]
    CATEGORIES = [
        ('grammar', 'Grammar'),
        ('vocabulary', 'Vocabulary'),
    ]
    title = models.CharField(max_length=128)
    exercise_type = models.CharField(max_length=50, choices=EXERCISE_TYPES)
    category = models.CharField(max_length=50, choices=CATEGORIES)
    level = models.CharField(max_length=10, choices=VocabularyCategory.LEVEL_CHOICES, default='A1')
    grammar_topic = models.ForeignKey(
        GrammarTopic, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='exercises'
    )
    vocabulary_category = models.ForeignKey(
        VocabularyCategory, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='exercises'
    )
    created_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Mashq'
        verbose_name_plural = 'Mashqlar'

    def __str__(self):
        return f"{self.title} ({self.exercise_type})"


class ExerciseQuestion(models.Model):
    """Mashq savollari"""
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    correct_answer = models.CharField(max_length=256)
    options = models.TextField(blank=True, null=True)       # JSON: ["opt1", "opt2", ...]
    gap_text = models.TextField(blank=True, null=True)       # "I ___ to school every day"
    matching_pairs = models.TextField(blank=True, null=True) # JSON: {"left": [...], "right": [...]}
    word_grid = models.TextField(blank=True, null=True)      # JSON formatda
    hidden_words = models.TextField(blank=True, null=True)   # JSON: ["word1", "word2"]
    order = models.IntegerField(default=0)
    points = models.IntegerField(default=10)

    class Meta:
        verbose_name = 'Savol'
        verbose_name_plural = 'Savollar'
        ordering = ['order']

    def __str__(self):
        return f"{self.exercise.title} - {self.question_text[:50]}"

    def get_options(self):
        if self.options:
            try:
                return json.loads(self.options)
            except (json.JSONDecodeError, TypeError):
                return []
        return []

    def get_hidden_words(self):
        if self.hidden_words:
            try:
                return json.loads(self.hidden_words)
            except (json.JSONDecodeError, TypeError):
                return []
        return []

    def get_matching_pairs(self):
        if self.matching_pairs:
            try:
                return json.loads(self.matching_pairs)
            except (json.JSONDecodeError, TypeError):
                return {'left': [], 'right': []}
        return {'left': [], 'right': []}

    def get_word_grid(self):
        if self.word_grid:
            try:
                return json.loads(self.word_grid)
            except (json.JSONDecodeError, TypeError):
                return []
        return []


class ExerciseResult(models.Model):
    """Foydalanuvchi mashq natijalari"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='edukids_results')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='results')
    score = models.IntegerField()
    total_questions = models.IntegerField()
    completed_date = models.DateTimeField(auto_now_add=True, db_index=True)
    time_spent = models.IntegerField(null=True, blank=True)  # soniyalarda

    class Meta:
        verbose_name = 'Natija'
        verbose_name_plural = 'Natijalar'
        ordering = ['-completed_date']

    def __str__(self):
        return f"{self.user.username} - {self.exercise.title}: {self.score}/{self.total_questions}"

    def percentage(self):
        if self.total_questions > 0:
            return round(self.score / self.total_questions * 100)
        return 0


# ============ PROGRESS TRACKING ============

class UserWordProgress(models.Model):
    """Foydalanuvchining so'z o'rganish progressi"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='word_progress')
    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='user_progress')
    learned = models.BooleanField(default=False)
    review_count = models.IntegerField(default=0)
    last_review = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'word')
        verbose_name = 'So\'z Progressi'
        verbose_name_plural = 'So\'z Progresslari'

    def __str__(self):
        return f"{self.user.username} - {self.word.english}"


class UserGrammarProgress(models.Model):
    """Foydalanuvchining grammar progressi"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='grammar_progress')
    grammar_topic = models.ForeignKey(GrammarTopic, on_delete=models.CASCADE, related_name='user_progress')
    completed = models.BooleanField(default=False)
    score = models.IntegerField(default=0)

    class Meta:
        unique_together = ('user', 'grammar_topic')
        verbose_name = 'Grammar Progressi'
        verbose_name_plural = 'Grammar Progresslari'

    def __str__(self):
        return f"{self.user.username} - {self.grammar_topic.title}"


# ============ QIZIQISHLARNI ANIQLASH MODELLARI ============

class InterestCategory(models.Model):
    """9-14 yoshli o'quvchilar uchun qiziqish sohalar"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='🌟')
    color = models.CharField(max_length=30, default='#667eea')
    career_suggestions = models.TextField(blank=True, null=True)  # JSON list
    order = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Qiziqish Kategoriyasi'
        verbose_name_plural = 'Qiziqish Kategoriyalari'
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.icon} {self.name}"

    def get_career_suggestions(self):
        if self.career_suggestions:
            try:
                return json.loads(self.career_suggestions)
            except (json.JSONDecodeError, TypeError):
                return []
        return []


class InterestQuestion(models.Model):
    """Qiziqishlarni aniqlash savollari (9-14 yosh)"""
    QUESTION_TYPES = [
        ('single', 'Bitta javob'),
        ('scale', '1-5 shkala'),
    ]
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='single')
    options = models.TextField(blank=True, null=True)          # JSON: [{"text":"...", "weights":{"science":3}}]
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Qiziqish Savoli'
        verbose_name_plural = 'Qiziqish Savollari'
        ordering = ['order']

    def __str__(self):
        return self.question_text[:80]

    def get_options(self):
        if self.options:
            try:
                return json.loads(self.options)
            except (json.JSONDecodeError, TypeError):
                return []
        return []


class InterestResult(models.Model):
    """O'quvchi qiziqishlari testi natijasi"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,
                             related_name='interest_results')
    session_key = models.CharField(max_length=64, blank=True)
    scores = models.TextField()          # JSON: {"Fan": 12, "San'at": 7, ...}
    top_category = models.ForeignKey(InterestCategory, on_delete=models.SET_NULL,
                                     null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    completed_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Qiziqish Natijasi'
        verbose_name_plural = 'Qiziqish Natijalari'
        ordering = ['-completed_date']

    def __str__(self):
        user_str = self.user.username if self.user else 'Mehmon'
        return f"{user_str} - {self.top_category}"

    def get_scores(self):
        try:
            return json.loads(self.scores)
        except (json.JSONDecodeError, TypeError):
            return {}


# ============ MANTIQIY FIKRLASH MODELLARI ============

class LogicExercise(models.Model):
    """9-14 yoshli o'quvchilar uchun mantiqiy mashqlar"""
    EXERCISE_TYPES = [
        ('pattern', 'Naqsh topish 🔢'),
        ('sequence', 'Ketma-ketlik 📐'),
        ('analogy', 'Analogiya 🔁'),
        ('spatial', 'Fazoviy fikrlash 🗺️'),
        ('math_logic', 'Matematik mantiq ➕'),
        ('deduction', 'Xulosa chiqarish 🔍'),
    ]
    DIFFICULTY_CHOICES = [
        (1, 'Oson ⭐'),
        (2, "O'rta ⭐⭐"),
        (3, 'Qiyin ⭐⭐⭐'),
    ]
    title = models.CharField(max_length=128)
    exercise_type = models.CharField(max_length=30, choices=EXERCISE_TYPES)
    difficulty = models.IntegerField(choices=DIFFICULTY_CHOICES, default=1)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='🧩')
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Mantiqiy Mashq'
        verbose_name_plural = 'Mantiqiy Mashqlar'
        ordering = ['difficulty', 'exercise_type']

    def __str__(self):
        return f"{self.icon} {self.title}"

    def question_count(self):
        return self.logic_questions.count()


class LogicQuestion(models.Model):
    """Mantiqiy mashq savoli"""
    exercise = models.ForeignKey(LogicExercise, on_delete=models.CASCADE,
                                 related_name='logic_questions')
    question_text = models.TextField()
    correct_answer = models.CharField(max_length=256)
    options = models.TextField(blank=True, null=True)   # JSON: ["A","B","C","D"]
    explanation = models.TextField(blank=True)           # javob tushuntirishi
    hint = models.TextField(blank=True)                  # maslahat
    points = models.IntegerField(default=10)
    order = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Mantiqiy Savol'
        verbose_name_plural = 'Mantiqiy Savollar'
        ordering = ['order']

    def __str__(self):
        return f"{self.exercise.title} - {self.question_text[:50]}"

    def get_options(self):
        if self.options:
            try:
                return json.loads(self.options)
            except (json.JSONDecodeError, TypeError):
                return []
        return []


class LogicResult(models.Model):
    """Mantiqiy mashq natijasi"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,
                             related_name='logic_results')
    exercise = models.ForeignKey(LogicExercise, on_delete=models.CASCADE,
                                 related_name='results')
    score = models.IntegerField()
    total_questions = models.IntegerField()
    time_spent = models.IntegerField(null=True, blank=True)  # soniyalarda
    completed_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Mantiq Natijasi'
        verbose_name_plural = 'Mantiq Natijalari'
        ordering = ['-completed_date']

    def __str__(self):
        user_str = self.user.username if self.user else 'Mehmon'
        return f"{user_str} - {self.exercise.title}: {self.score}/{self.total_questions}"

    def percentage(self):
        if self.total_questions > 0:
            return round(self.score / self.total_questions * 100)
        return 0

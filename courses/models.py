from django.db import models
from django.contrib.auth.models import User


class Module(models.Model):

    LEVEL_CHOICES = [
        ('iniciante', 'Iniciante'),
        ('basico', 'Básico'),
        ('intermediario', 'Intermediário'),
        ('avancado', 'Avançado'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveSmallIntegerField(unique=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    thumbnail = models.ImageField(upload_to='modules/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Módulo'
        verbose_name_plural = 'Módulos'
        ordering = ['order']

    def __str__(self):
        return f'Módulo {self.order:02d} — {self.title}'

    @property
    def total_lessons(self):
        return self.lessons.filter(is_active=True).count()

    @property
    def total_duration_minutes(self):
        return self.lessons.filter(is_active=True).aggregate(
            total=models.Sum('duration_minutes')
        )['total'] or 0


class Lesson(models.Model):

    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    objectives = models.TextField(blank=True)
    video_url = models.URLField(blank=True)
    video_file = models.FileField(upload_to='lessons/videos/', blank=True, null=True)
    duration_minutes = models.PositiveSmallIntegerField(default=0)
    order = models.PositiveSmallIntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Aula'
        verbose_name_plural = 'Aulas'
        ordering = ['module__order', 'order']
        unique_together = ('module', 'order')

    def __str__(self):
        return f'Aula {self.order} — {self.title} ({self.module.title})'


class Material(models.Model):

    FILE_TYPE_CHOICES = [
        ('pdf', 'PDF'),
        ('mp3', 'Áudio MP3'),
        ('mp4', 'Vídeo MP4'),
        ('xlsx', 'Planilha'),
        ('other', 'Outro'),
    ]

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='materials')
    name = models.CharField(max_length=200)
    file = models.FileField(upload_to='materials/')
    file_type = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES, default='pdf')
    size_kb = models.PositiveIntegerField(default=0)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = 'Material'
        verbose_name_plural = 'Materiais'
        ordering = ['order']

    def __str__(self):
        return f'{self.name} ({self.lesson.title})'


class Exercise(models.Model):

    DIFFICULTY_CHOICES = [
        ('easy', 'Fácil'),
        ('medium', 'Médio'),
        ('hard', 'Difícil'),
    ]

    TYPE_CHOICES = [
        ('practice', 'Prática'),
        ('quiz', 'Múltipla Escolha'),
    ]

    OPTION_CHOICES = [
        ('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'),
    ]

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='exercises')
    number = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    exercise_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='practice')
    option_a = models.CharField(max_length=300, blank=True)
    option_b = models.CharField(max_length=300, blank=True)
    option_c = models.CharField(max_length=300, blank=True)
    option_d = models.CharField(max_length=300, blank=True)
    correct_option = models.CharField(max_length=1, choices=OPTION_CHOICES, blank=True)

    class Meta:
        verbose_name = 'Exercício'
        verbose_name_plural = 'Exercícios'
        ordering = ['number']
        unique_together = ('lesson', 'number')

    def __str__(self):
        return f'Exercício {self.number} — {self.title} ({self.lesson.title})'


class Question(models.Model):

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='questions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Pergunta'
        verbose_name_plural = 'Perguntas'
        ordering = ['-created_at']

    def __str__(self):
        return f'Pergunta de {self.user.username} em "{self.lesson.title}"'


class Answer(models.Model):

    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers')
    text = models.TextField()
    is_professor_answer = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Resposta'
        verbose_name_plural = 'Respostas'
        ordering = ['created_at']

    def __str__(self):
        label = 'Professor' if self.is_professor_answer else self.user.username
        return f'Resposta de {label} para "{self.question}"'

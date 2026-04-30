from django.db import models
from django.contrib.auth.models import User
from courses.models import Module, Lesson


class LessonProgress(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progress')
    completed = models.BooleanField(default=False)
    watch_time_seconds = models.PositiveIntegerField(default=0)
    resume_position = models.PositiveIntegerField(default=0)
    completed_at = models.DateTimeField(blank=True, null=True)
    last_watched_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Progresso de Aula'
        verbose_name_plural = 'Progresso de Aulas'
        unique_together = ('user', 'lesson')

    def __str__(self):
        status = 'Concluída' if self.completed else 'Em progresso'
        return f'{self.user.username} — {self.lesson.title} [{status}]'


class ModuleProgress(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='module_progress')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='progress')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'Progresso de Módulo'
        verbose_name_plural = 'Progresso de Módulos'
        unique_together = ('user', 'module')

    def __str__(self):
        return f'{self.user.username} — {self.module.title}'

    @property
    def completed_lessons(self):
        return LessonProgress.objects.filter(
            user=self.user,
            lesson__module=self.module,
            completed=True,
        ).count()

    @property
    def percentage(self):
        total = self.module.total_lessons
        if total == 0:
            return 0
        return round((self.completed_lessons / total) * 100)

    @property
    def is_complete(self):
        return self.completed_at is not None


class StudyStreak(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='streak')
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    last_study_date = models.DateField(blank=True, null=True)

    class Meta:
        verbose_name = 'Sequência de Estudo'
        verbose_name_plural = 'Sequências de Estudo'

    def __str__(self):
        return f'{self.user.username} — {self.current_streak} dias'


class ActivityLog(models.Model):

    TYPE_CHOICES = [
        ('lesson_complete', 'Aula Concluída'),
        ('module_start', 'Módulo Iniciado'),
        ('module_complete', 'Módulo Concluído'),
        ('achievement_unlock', 'Conquista Desbloqueada'),
        ('streak_update', 'Sequência Atualizada'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    activity_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    description = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Log de Atividade'
        verbose_name_plural = 'Logs de Atividade'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} — {self.description}'

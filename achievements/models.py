from django.db import models
from django.contrib.auth.models import User


class Achievement(models.Model):

    CONDITION_CHOICES = [
        ('first_lesson', 'Primeira aula concluída'),
        ('module_complete', 'Módulo concluído'),
        ('lessons_count', 'Total de aulas assistidas'),
        ('modules_count', 'Total de módulos concluídos'),
        ('streak_days', 'Sequência de dias'),
        ('early_access', 'Acesso antes das 6h'),
        ('all_modules', 'Todos os módulos concluídos'),
        ('specific_module', 'Módulo específico concluído'),
    ]

    title = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    icon = models.CharField(max_length=10)
    condition_type = models.CharField(max_length=30, choices=CONDITION_CHOICES)
    condition_value = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Conquista'
        verbose_name_plural = 'Conquistas'
        ordering = ['condition_type', 'condition_value']

    def __str__(self):
        return f'{self.icon} {self.title}'


class UserAchievement(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE, related_name='users')
    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Conquista do Usuário'
        verbose_name_plural = 'Conquistas dos Usuários'
        unique_together = ('user', 'achievement')
        ordering = ['-unlocked_at']

    def __str__(self):
        return f'{self.user.username} desbloqueou "{self.achievement.title}"'

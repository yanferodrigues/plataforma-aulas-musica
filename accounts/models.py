from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):

    INSTRUMENT_CHOICES = [
        ('violao', 'Violão'),
        ('guitarra', 'Guitarra'),
        ('piano', 'Piano / Teclado'),
        ('baixo', 'Baixo'),
        ('bateria', 'Bateria / Percussão'),
        ('voz', 'Voz / Canto'),
        ('outro', 'Outro'),
    ]

    LEVEL_CHOICES = [
        ('iniciante', 'Iniciante'),
        ('basico', 'Básico'),
        ('intermediario', 'Intermediário'),
        ('avancado', 'Avançado'),
    ]

    GOAL_CHOICES = [
        ('hobby', 'Tocar por hobby'),
        ('profissional', 'Me tornar profissional'),
        ('producao', 'Produzir minhas músicas'),
        ('teoria', 'Aprender teoria musical'),
    ]

    PLAN_CHOICES = [
        ('free', 'Gratuito'),
        ('pro', 'Pro'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    instrument = models.CharField(max_length=20, choices=INSTRUMENT_CHOICES, blank=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='iniciante')
    goal = models.CharField(max_length=20, choices=GOAL_CHOICES, blank=True)
    plan = models.CharField(max_length=10, choices=PLAN_CHOICES, default='free')
    is_public = models.BooleanField(default=False)
    share_usage_data = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'

    def __str__(self):
        return f'Perfil de {self.user.get_full_name() or self.user.username}'


class NotificationSettings(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_settings')
    progress_emails = models.BooleanField(default=True)
    study_reminders = models.BooleanField(default=True)
    new_lessons = models.BooleanField(default=False)
    achievements_unlocked = models.BooleanField(default=True)
    newsletters = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Configurações de Notificação'
        verbose_name_plural = 'Configurações de Notificação'

    def __str__(self):
        return f'Notificações de {self.user.username}'


class PlaybackSettings(models.Model):

    QUALITY_CHOICES = [
        ('auto', 'Auto'),
        ('1080p', '1080p'),
        ('720p', '720p'),
        ('480p', '480p'),
        ('360p', '360p'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='playback_settings')
    autoplay = models.BooleanField(default=True)
    default_captions = models.BooleanField(default=False)
    video_quality = models.CharField(max_length=10, choices=QUALITY_CHOICES, default='720p')

    class Meta:
        verbose_name = 'Configurações de Reprodução'
        verbose_name_plural = 'Configurações de Reprodução'

    def __str__(self):
        return f'Reprodução de {self.user.username}'

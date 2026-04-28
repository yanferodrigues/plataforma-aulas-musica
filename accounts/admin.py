from django.contrib import admin
from .models import Profile, NotificationSettings, PlaybackSettings


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'instrument', 'level', 'plan', 'created_at')
    list_filter = ('plan', 'level', 'instrument')
    search_fields = ('user__username', 'user__email', 'user__first_name')
    raw_id_fields = ('user',)


@admin.register(NotificationSettings)
class NotificationSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'progress_emails', 'study_reminders', 'achievements_unlocked')
    raw_id_fields = ('user',)


@admin.register(PlaybackSettings)
class PlaybackSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'autoplay', 'default_captions', 'video_quality')
    raw_id_fields = ('user',)

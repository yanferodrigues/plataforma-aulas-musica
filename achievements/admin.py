from django.contrib import admin
from .models import Achievement, UserAchievement


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('icon', 'title', 'condition_type', 'condition_value', 'is_active')
    list_filter = ('condition_type', 'is_active')
    search_fields = ('title', 'description')


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'achievement', 'unlocked_at')
    list_filter = ('achievement',)
    search_fields = ('user__username', 'achievement__title')
    raw_id_fields = ('user',)

from django.contrib import admin
from .models import LessonProgress, ModuleProgress, StudyStreak, ActivityLog


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'completed', 'watch_time_seconds', 'completed_at')
    list_filter = ('completed', 'lesson__module')
    search_fields = ('user__username', 'lesson__title')
    raw_id_fields = ('user', 'lesson')


@admin.register(ModuleProgress)
class ModuleProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'module', 'percentage', 'is_complete', 'started_at')
    list_filter = ('module',)
    search_fields = ('user__username', 'module__title')
    raw_id_fields = ('user', 'module')


@admin.register(StudyStreak)
class StudyStreakAdmin(admin.ModelAdmin):
    list_display = ('user', 'current_streak', 'longest_streak', 'last_study_date')
    search_fields = ('user__username',)
    raw_id_fields = ('user',)


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'description', 'created_at')
    list_filter = ('activity_type',)
    search_fields = ('user__username', 'description')
    raw_id_fields = ('user',)

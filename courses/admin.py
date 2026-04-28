from django.contrib import admin
from .models import Module, Lesson, Material, Exercise, Question, Answer


class LessonInline(admin.TabularInline):
    model = Lesson
    fields = ('order', 'title', 'duration_minutes', 'is_active')
    extra = 0
    ordering = ('order',)


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('order', 'title', 'level', 'total_lessons', 'is_active')
    list_filter = ('level', 'is_active')
    search_fields = ('title',)
    ordering = ('order',)
    inlines = [LessonInline]


class MaterialInline(admin.TabularInline):
    model = Material
    fields = ('order', 'name', 'file_type', 'size_kb')
    extra = 0


class ExerciseInline(admin.TabularInline):
    model = Exercise
    fields = ('number', 'title', 'difficulty')
    extra = 0


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('order', 'title', 'module', 'duration_minutes', 'is_active')
    list_filter = ('module', 'is_active')
    search_fields = ('title', 'module__title')
    ordering = ('module__order', 'order')
    inlines = [MaterialInline, ExerciseInline]


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('name', 'lesson', 'file_type', 'size_kb')
    list_filter = ('file_type',)
    search_fields = ('name', 'lesson__title')


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('number', 'title', 'lesson', 'difficulty')
    list_filter = ('difficulty', 'lesson__module')
    search_fields = ('title', 'lesson__title')


class AnswerInline(admin.TabularInline):
    model = Answer
    fields = ('user', 'text', 'is_professor_answer', 'created_at')
    readonly_fields = ('created_at',)
    extra = 0


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'created_at')
    list_filter = ('lesson__module',)
    search_fields = ('user__username', 'text', 'lesson__title')
    inlines = [AnswerInline]

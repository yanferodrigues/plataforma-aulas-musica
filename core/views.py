from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from courses.models import Module, Lesson, Material, Exercise
from achievements.models import Achievement


def index(request):
    return render(request, 'index.html')


def _superuser(user):
    return user.is_active and user.is_superuser


def superuser_required(fn):
    return login_required(
        user_passes_test(_superuser, login_url='accounts:login')(fn),
        login_url='accounts:login',
    )


@superuser_required
def studio(request):
    context = {
        'modules': Module.objects.prefetch_related('lessons').order_by('order'),
        'lessons': Lesson.objects.select_related('module').order_by('module__order', 'order'),
        'achievements': Achievement.objects.all(),
        'users': User.objects.order_by('-date_joined'),
        'level_choices': Module.LEVEL_CHOICES,
        'condition_choices': Achievement.CONDITION_CHOICES,
        'total_users': User.objects.count(),
        'total_modules': Module.objects.count(),
        'total_lessons': Lesson.objects.count(),
        'total_achievements': Achievement.objects.count(),
    }
    return render(request, 'studio.html', context)


# ── MÓDULOS ──────────────────────────────────────────────────

@superuser_required
def studio_module_save(request, pk=None):
    if request.method != 'POST':
        return redirect('core:studio')

    data = {
        'title': request.POST.get('title', '').strip(),
        'description': request.POST.get('description', '').strip(),
        'order': int(request.POST.get('order') or 0),
        'level': request.POST.get('level', 'iniciante'),
        'is_active': request.POST.get('is_active') == 'on',
    }

    if pk:
        obj = get_object_or_404(Module, pk=pk)
        for k, v in data.items():
            setattr(obj, k, v)
        if 'thumbnail' in request.FILES:
            obj.thumbnail = request.FILES['thumbnail']
        obj.save()
        messages.success(request, f'Módulo "{obj.title}" atualizado.')
    else:
        obj = Module(**data)
        if 'thumbnail' in request.FILES:
            obj.thumbnail = request.FILES['thumbnail']
        obj.save()
        messages.success(request, f'Módulo "{obj.title}" criado.')

    return redirect('core:studio')


@superuser_required
def studio_module_delete(request, pk):
    obj = get_object_or_404(Module, pk=pk)
    name = obj.title
    obj.delete()
    messages.success(request, f'Módulo "{name}" excluído.')
    return redirect('core:studio')


# ── AULAS ────────────────────────────────────────────────────

@superuser_required
def studio_lesson_save(request, pk=None):
    if request.method != 'POST':
        return redirect('core:studio')

    module = get_object_or_404(Module, pk=request.POST.get('module'))
    data = {
        'module': module,
        'title': request.POST.get('title', '').strip(),
        'description': request.POST.get('description', '').strip(),
        'objectives': request.POST.get('objectives', '').strip(),
        'video_url': request.POST.get('video_url', '').strip(),
        'duration_minutes': int(request.POST.get('duration_minutes') or 0),
        'order': int(request.POST.get('order') or 1),
        'is_active': request.POST.get('is_active') == 'on',
    }

    if pk:
        obj = get_object_or_404(Lesson, pk=pk)
        for k, v in data.items():
            setattr(obj, k, v)
        obj.save()
        messages.success(request, f'Aula "{obj.title}" atualizada.')
    else:
        obj = Lesson.objects.create(**data)
        messages.success(request, f'Aula "{obj.title}" criada.')

    return redirect('core:studio')


@superuser_required
def studio_lesson_delete(request, pk):
    obj = get_object_or_404(Lesson, pk=pk)
    name = obj.title
    obj.delete()
    messages.success(request, f'Aula "{name}" excluída.')
    return redirect('core:studio')


# ── CONQUISTAS ───────────────────────────────────────────────

@superuser_required
def studio_achievement_save(request, pk=None):
    if request.method != 'POST':
        return redirect('core:studio')

    data = {
        'title': request.POST.get('title', '').strip(),
        'description': request.POST.get('description', '').strip(),
        'icon': request.POST.get('icon', '🏆').strip(),
        'condition_type': request.POST.get('condition_type', 'first_lesson'),
        'condition_value': int(request.POST.get('condition_value') or 1),
        'is_active': request.POST.get('is_active') == 'on',
    }

    if pk:
        obj = get_object_or_404(Achievement, pk=pk)
        for k, v in data.items():
            setattr(obj, k, v)
        obj.save()
        messages.success(request, f'Conquista "{obj.title}" atualizada.')
    else:
        obj = Achievement.objects.create(**data)
        messages.success(request, f'Conquista "{obj.title}" criada.')

    return redirect('core:studio')


@superuser_required
def studio_achievement_delete(request, pk):
    obj = get_object_or_404(Achievement, pk=pk)
    name = obj.title
    obj.delete()
    messages.success(request, f'Conquista "{name}" excluída.')
    return redirect('core:studio')

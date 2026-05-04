from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import IntegrityError
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
        'materials': Material.objects.select_related('lesson__module').order_by('lesson__module__order', 'lesson__order', 'order'),
        'exercises': Exercise.objects.select_related('lesson__module').order_by('lesson__module__order', 'lesson__order', 'number'),
        'total_modules': Module.objects.count(),
        'total_lessons': Lesson.objects.count(),
        'total_achievements': Achievement.objects.count(),
        'total_materials': Material.objects.count(),
        'total_exercises': Exercise.objects.count(),
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

    try:
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
    except IntegrityError:
        messages.error(request, f'Já existe um módulo com a ordem {data["order"]}. Escolha um número diferente.')

    return redirect('core:studio')


@superuser_required
def studio_module_delete(request, pk):
    obj = get_object_or_404(Module, pk=pk)
    name = obj.title
    obj.delete()
    messages.success(request, f'Módulo "{name}" excluído.')
    return redirect('core:studio')


# ── AULAS ────────────────────────────────────────────────────

def _notify_new_lesson(lesson):
    from accounts.views import send_notification
    from django.contrib.auth.models import User as _User
    users = _User.objects.filter(
        notification_settings__new_lessons=True,
        is_active=True,
        is_superuser=False,
    )
    for user in users:
        send_notification(
            user=user,
            subject=f'Nova aula disponível: {lesson.title}',
            message=(
                f'Uma nova aula foi adicionada ao módulo "{lesson.module.title}":\n\n'
                f'{lesson.title}\n\n'
                f'Acesse agora e continue aprendendo!\n\n— Equipe MUSILAB'
            ),
        )


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
        'roteiro': request.POST.get('roteiro', '').strip(),
        'video_url': request.POST.get('video_url', '').strip(),
        'duration_minutes': int(request.POST.get('duration_minutes') or 0),
        'order': int(request.POST.get('order') or 1),
        'is_active': request.POST.get('is_active') == 'on',
    }

    try:
        if pk:
            obj = get_object_or_404(Lesson, pk=pk)
            was_active = obj.is_active
            for k, v in data.items():
                setattr(obj, k, v)
            if 'video_file' in request.FILES:
                obj.video_file = request.FILES['video_file']
            obj.save()
            messages.success(request, f'Aula "{obj.title}" atualizada.')
            if not was_active and obj.is_active:
                _notify_new_lesson(obj)
        else:
            if 'video_file' in request.FILES:
                data['video_file'] = request.FILES['video_file']
            obj = Lesson.objects.create(**data)
            messages.success(request, f'Aula "{obj.title}" criada.')
            if obj.is_active:
                _notify_new_lesson(obj)
    except IntegrityError:
        messages.error(request, f'Já existe uma aula com a ordem {data["order"]} neste módulo. Escolha um número diferente.')

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


# ── MATERIAIS ────────────────────────────────────────────────

@superuser_required
def studio_material_save(request, pk=None):
    if request.method != 'POST':
        return redirect('core:studio')

    lesson = get_object_or_404(Lesson, pk=request.POST.get('lesson'))
    data = {
        'lesson': lesson,
        'name': request.POST.get('name', '').strip(),
        'file_type': request.POST.get('file_type', 'other'),
        'order': int(request.POST.get('order') or 0),
    }

    if pk:
        obj = get_object_or_404(Material, pk=pk)
        for k, v in data.items():
            setattr(obj, k, v)
        if 'file' in request.FILES:
            obj.file = request.FILES['file']
            obj.size_kb = request.FILES['file'].size // 1024
        obj.save()
        messages.success(request, f'Material "{obj.name}" atualizado.')
    else:
        file = request.FILES.get('file')
        if file:
            data['file'] = file
            data['size_kb'] = file.size // 1024
        obj = Material.objects.create(**data)
        messages.success(request, f'Material "{obj.name}" criado.')

    return redirect('core:studio')


@superuser_required
def studio_material_delete(request, pk):
    obj = get_object_or_404(Material, pk=pk)
    name = obj.name
    obj.delete()
    messages.success(request, f'Material "{name}" excluído.')
    return redirect('core:studio')


# ── EXERCÍCIOS ───────────────────────────────────────────────

@superuser_required
def studio_exercise_save(request, pk=None):
    if request.method != 'POST':
        return redirect('core:studio')

    lesson = get_object_or_404(Lesson, pk=request.POST.get('lesson'))
    ex_type = request.POST.get('exercise_type', 'practice')
    data = {
        'lesson': lesson,
        'number': int(request.POST.get('number') or 1),
        'title': request.POST.get('title', '').strip(),
        'description': request.POST.get('description', '').strip(),
        'difficulty': request.POST.get('difficulty', 'easy'),
        'exercise_type': ex_type,
        'option_a': request.POST.get('option_a', '').strip() if ex_type == 'quiz' else '',
        'option_b': request.POST.get('option_b', '').strip() if ex_type == 'quiz' else '',
        'option_c': request.POST.get('option_c', '').strip() if ex_type == 'quiz' else '',
        'option_d': request.POST.get('option_d', '').strip() if ex_type == 'quiz' else '',
        'correct_option': request.POST.get('correct_option', '').strip() if ex_type == 'quiz' else '',
    }

    try:
        if pk:
            obj = get_object_or_404(Exercise, pk=pk)
            for k, v in data.items():
                setattr(obj, k, v)
            obj.save()
            messages.success(request, f'Exercício "{obj.title}" atualizado.')
        else:
            obj = Exercise.objects.create(**data)
            messages.success(request, f'Exercício "{obj.title}" criado.')
    except IntegrityError:
        messages.error(request, f'Já existe um exercício com o número {data["number"]} nesta aula. Escolha um número diferente.')

    return redirect('core:studio')


@superuser_required
def studio_exercise_delete(request, pk):
    obj = get_object_or_404(Exercise, pk=pk)
    name = obj.title
    obj.delete()
    messages.success(request, f'Exercício "{name}" excluído.')
    return redirect('core:studio')


# ── USUÁRIOS ─────────────────────────────────────────────────

@superuser_required
def studio_user_delete(request, pk):
    obj = get_object_or_404(User, pk=pk)
    if obj == request.user:
        messages.error(request, 'Você não pode excluir sua própria conta.')
        return redirect('core:studio')
    if obj.is_superuser:
        messages.error(request, 'Não é possível excluir outro superusuário.')
        return redirect('core:studio')
    name = obj.get_full_name() or obj.username
    obj.delete()
    messages.success(request, f'Usuário "{name}" excluído.')
    return redirect('core:studio')


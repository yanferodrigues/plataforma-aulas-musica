from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from courses.models import Module, Lesson, Question
from progress.models import LessonProgress, ModuleProgress


def _fmt_duration(minutes):
    minutes = int(minutes or 0)
    h, m = divmod(minutes, 60)
    if h and m:
        return f'{h}h {m:02d}min'
    if h:
        return f'{h}h'
    return f'{m}min'


def _embed_url(url):
    if not url:
        return None
    if 'youtube.com/watch?v=' in url:
        vid = url.split('v=')[1].split('&')[0]
        return f'https://www.youtube.com/embed/{vid}?rel=0'
    if 'youtu.be/' in url:
        vid = url.split('youtu.be/')[1].split('?')[0]
        return f'https://www.youtube.com/embed/{vid}?rel=0'
    return url


def _module_btn(pct, completed):
    if completed:
        return 'Revisar módulo'
    if pct > 0:
        return 'Continuar'
    return 'Começar módulo'


def _build_modules_data(modules, progress_map):
    result = []
    for i, m in enumerate(modules):
        mp = progress_map.get(m.pk)
        pct = mp.percentage if mp else 0
        done = mp.is_complete if mp else False
        result.append({
            'module': m,
            'percentage': pct,
            'completed': done,
            'color_class': f'mod-bg-{(i % 6) + 1}',
            'duration_display': _fmt_duration(m.total_duration_minutes),
            'btn_text': _module_btn(pct, done),
        })
    return result


@login_required(login_url='accounts:login')
def dashboard(request):
    user = request.user
    modules = list(Module.objects.filter(is_active=True).prefetch_related('lessons').order_by('order'))
    progress_map = {mp.module_id: mp for mp in ModuleProgress.objects.filter(user=user)}
    modules_data = _build_modules_data(modules, progress_map)

    last_lp = (
        LessonProgress.objects
        .filter(user=user, completed=False)
        .select_related('lesson__module')
        .order_by('-last_watched_at')
        .first()
    ) or (
        LessonProgress.objects
        .filter(user=user)
        .select_related('lesson__module')
        .order_by('-last_watched_at')
        .first()
    )

    continue_pct = 0
    remaining_min = None
    if last_lp and last_lp.lesson.duration_minutes:
        total_sec = last_lp.lesson.duration_minutes * 60
        continue_pct = min(100, round(last_lp.watch_time_seconds / total_sec * 100)) if total_sec else 0
        watched_min = last_lp.watch_time_seconds // 60
        remaining_min = max(0, last_lp.lesson.duration_minutes - watched_min)

    context = {
        'modules': modules_data,
        'last_progress': last_lp,
        'continue_pct': continue_pct,
        'remaining_min': remaining_min,
    }
    return render(request, 'dashboard.html', context)


@login_required(login_url='accounts:login')
def module_list(request):
    user = request.user
    modules = list(Module.objects.filter(is_active=True).prefetch_related('lessons').order_by('order'))
    progress_map = {mp.module_id: mp for mp in ModuleProgress.objects.filter(user=user)}
    modules_data = _build_modules_data(modules, progress_map)

    total_lessons = sum(m.total_lessons for m in modules)
    total_minutes = sum(m.total_duration_minutes for m in modules)

    context = {
        'modules': modules_data,
        'total_modules': len(modules),
        'total_lessons': total_lessons,
        'total_duration': _fmt_duration(total_minutes),
    }
    return render(request, 'modules.html', context)


@login_required(login_url='accounts:login')
def module_detail(request, pk):
    module = get_object_or_404(Module, pk=pk, is_active=True)
    completed_ids = set(
        LessonProgress.objects.filter(user=request.user, completed=True)
        .values_list('lesson_id', flat=True)
    )
    lesson = (
        module.lessons.filter(is_active=True).exclude(pk__in=completed_ids).order_by('order').first()
        or module.lessons.filter(is_active=True).order_by('order').first()
    )
    if lesson:
        return redirect('courses:lesson_detail', module_pk=module.pk, pk=lesson.pk)
    return redirect('courses:module_list')


@login_required(login_url='accounts:login')
def lesson_detail(request, module_pk, pk):
    module = get_object_or_404(Module, pk=module_pk, is_active=True)
    lesson = get_object_or_404(Lesson, pk=pk, module=module, is_active=True)

    if request.method == 'POST':
        text = request.POST.get('question_text', '').strip()
        if text:
            Question.objects.create(lesson=lesson, user=request.user, text=text)
        return redirect('courses:lesson_detail', module_pk=module_pk, pk=pk)

    all_lessons = list(module.lessons.filter(is_active=True).order_by('order'))
    lp_map = {
        lp.lesson_id: lp
        for lp in LessonProgress.objects.filter(user=request.user, lesson__in=all_lessons)
    }

    lessons_status = []
    current_idx = None
    for i, l in enumerate(all_lessons):
        lp = lp_map.get(l.pk)
        if l.pk == lesson.pk:
            current_idx = i
        lessons_status.append({
            'lesson': l,
            'completed': lp.completed if lp else False,
            'is_current': l.pk == lesson.pk,
        })

    completed_count = sum(1 for x in lessons_status if x['completed'])
    total_count = len(all_lessons)
    module_pct = round(completed_count / total_count * 100) if total_count else 0

    prev_lesson = all_lessons[current_idx - 1] if current_idx and current_idx > 0 else None
    next_lesson = all_lessons[current_idx + 1] if current_idx is not None and current_idx < total_count - 1 else None

    objectives_list = [o.strip() for o in lesson.objectives.split('\n') if o.strip()] if lesson.objectives else []

    context = {
        'module': module,
        'lesson': lesson,
        'lessons_status': lessons_status,
        'completed_count': completed_count,
        'total_count': total_count,
        'module_pct': module_pct,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson,
        'objectives_list': objectives_list,
        'materials': lesson.materials.all(),
        'exercises': lesson.exercises.all(),
        'questions': lesson.questions.select_related('user').prefetch_related('answers__user').all(),
        'embed_url': _embed_url(lesson.video_url),
    }
    return render(request, 'lesson.html', context)

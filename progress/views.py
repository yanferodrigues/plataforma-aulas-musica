from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
from courses.models import Module, Lesson
from progress.models import LessonProgress, ModuleProgress, StudyStreak, ActivityLog


def _time_label(dt):
    delta = timezone.now() - dt
    days = delta.days
    if days == 0:
        return 'Hoje'
    if days == 1:
        return 'Ontem'
    return f'Há {days} dias'


@login_required(login_url='accounts:login')
def progress(request):
    user = request.user
    modules = list(Module.objects.filter(is_active=True).order_by('order').prefetch_related('lessons'))

    mp_list = list(ModuleProgress.objects.filter(user=user).select_related('module'))
    progress_map = {mp.module_id: mp for mp in mp_list}

    total_lessons = Lesson.objects.filter(module__is_active=True, is_active=True).count()
    completed_lessons = LessonProgress.objects.filter(user=user, completed=True).count()
    completed_modules = sum(1 for mp in mp_list if mp.is_complete)

    streak_obj = StudyStreak.objects.filter(user=user).first()
    streak = streak_obj.current_streak if streak_obj else 0

    total_seconds = (
        LessonProgress.objects.filter(user=user)
        .aggregate(total=Sum('watch_time_seconds'))['total'] or 0
    )
    total_hours = total_seconds // 3600

    overall_pct = round(completed_lessons / total_lessons * 100) if total_lessons else 0

    raw_activities = list(ActivityLog.objects.filter(user=user).order_by('-created_at')[:10])
    activities = [{'log': a, 'time_label': _time_label(a.created_at)} for a in raw_activities]

    modules_data = []
    for m in modules:
        mp = progress_map.get(m.pk)
        pct = mp.percentage if mp else 0
        is_complete = mp.is_complete if mp else False
        has_started = mp is not None
        modules_data.append({
            'module': m,
            'percentage': pct,
            'is_complete': is_complete,
            'has_started': has_started,
        })

    context = {
        'total_hours': total_hours,
        'completed_lessons': completed_lessons,
        'total_lessons': total_lessons,
        'completed_modules': completed_modules,
        'total_modules': len(modules),
        'streak': streak,
        'overall_pct': overall_pct,
        'modules_data': modules_data,
        'activities': activities,
    }
    return render(request, 'progress.html', context)

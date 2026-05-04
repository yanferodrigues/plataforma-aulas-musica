import datetime
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum
from django.utils import timezone
from courses.models import Module, Lesson
from progress.models import LessonProgress, ModuleProgress, StudyStreak, ActivityLog, ExerciseAnswer
from achievements.models import Achievement, UserAchievement
from courses.models import Exercise


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


# ── Helpers ────────────────────────────────────────────────────────────────────

def _check_achievements(user, newly_completed_module=None):
    from accounts.views import send_notification

    unlocked_ids = set(
        UserAchievement.objects.filter(user=user).values_list('achievement_id', flat=True)
    )
    pending = list(Achievement.objects.filter(is_active=True).exclude(id__in=unlocked_ids))
    if not pending:
        return

    completed_lessons = None
    completed_modules = None
    total_modules = None
    streak = None
    now_local = timezone.localtime(timezone.now())

    for achievement in pending:
        unlocked = False
        ct = achievement.condition_type
        cv = achievement.condition_value

        if ct == 'first_lesson':
            if completed_lessons is None:
                completed_lessons = LessonProgress.objects.filter(user=user, completed=True).count()
            unlocked = completed_lessons >= 1

        elif ct == 'lessons_count':
            if completed_lessons is None:
                completed_lessons = LessonProgress.objects.filter(user=user, completed=True).count()
            unlocked = completed_lessons >= cv

        elif ct == 'module_complete':
            if completed_modules is None:
                completed_modules = ModuleProgress.objects.filter(user=user, completed_at__isnull=False).count()
            unlocked = completed_modules >= 1

        elif ct == 'modules_count':
            if completed_modules is None:
                completed_modules = ModuleProgress.objects.filter(user=user, completed_at__isnull=False).count()
            unlocked = completed_modules >= cv

        elif ct == 'streak_days':
            if streak is None:
                streak_obj = StudyStreak.objects.filter(user=user).first()
                streak = streak_obj.current_streak if streak_obj else 0
            unlocked = streak >= cv

        elif ct == 'early_access':
            unlocked = now_local.hour < 6

        elif ct == 'all_modules':
            if total_modules is None:
                total_modules = Module.objects.filter(is_active=True).count()
            if completed_modules is None:
                completed_modules = ModuleProgress.objects.filter(user=user, completed_at__isnull=False).count()
            unlocked = total_modules > 0 and completed_modules >= total_modules

        elif ct == 'specific_module':
            if newly_completed_module is not None:
                unlocked = newly_completed_module.pk == cv
            else:
                unlocked = ModuleProgress.objects.filter(
                    user=user, module_id=cv, completed_at__isnull=False
                ).exists()

        if unlocked:
            _, created = UserAchievement.objects.get_or_create(user=user, achievement=achievement)
            if created:
                ActivityLog.objects.create(
                    user=user,
                    activity_type='achievement_unlock',
                    description=f'Conquista "{achievement.title}" desbloqueada',
                )
                send_notification(
                    user=user,
                    subject=f'Conquista desbloqueada: {achievement.title}',
                    message=f'{achievement.icon} Você desbloqueou a conquista "{achievement.title}"!\n\n{achievement.description}',
                    pref_key='achievements_unlocked',
                )


def _all_exercises_done(user, lesson):
    total = lesson.exercises.count()
    if total == 0:
        return True
    done = ExerciseAnswer.objects.filter(user=user, exercise__lesson=lesson).count()
    return done >= total


def _try_complete_lesson(user, lp):
    """Marca a aula como concluída se vídeo assistido e todos os exercícios respondidos."""
    if lp.completed:
        return False
    if not lp.video_watched:
        return False
    if not _all_exercises_done(user, lp.lesson):
        return False
    lp.completed = True
    lp.completed_at = timezone.now()
    lp.save()
    ActivityLog.objects.create(
        user=user,
        activity_type='lesson_complete',
        description=f'Aula "{lp.lesson.title}" concluída',
    )
    _update_streak(user)
    ModuleProgress.objects.get_or_create(user=user, module=lp.lesson.module)
    _check_module_completion(user, lp.lesson.module)
    _check_achievements(user)
    return True


def _update_streak(user):
    today = timezone.localdate()
    streak, _ = StudyStreak.objects.get_or_create(user=user)
    if streak.last_study_date == today:
        return
    if streak.last_study_date == today - datetime.timedelta(days=1):
        streak.current_streak += 1
    else:
        streak.current_streak = 1
    streak.last_study_date = today
    streak.longest_streak = max(streak.longest_streak, streak.current_streak)
    streak.save()


def _check_module_completion(user, module):
    total = module.total_lessons
    if total == 0:
        return
    done = LessonProgress.objects.filter(user=user, lesson__module=module, completed=True).count()
    if done < total:
        return
    mp, _ = ModuleProgress.objects.get_or_create(user=user, module=module)
    if not mp.completed_at:
        mp.completed_at = timezone.now()
        mp.save()
        ActivityLog.objects.create(
            user=user,
            activity_type='module_complete',
            description=f'Módulo "{module.title}" concluído',
        )
        _check_achievements(user, newly_completed_module=module)


# ── API endpoint ───────────────────────────────────────────────────────────────

@login_required(login_url='accounts:login')
def submit_exercise(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'method not allowed'}, status=405)

    try:
        exercise_id = int(request.POST.get('exercise_id', 0))
    except (ValueError, TypeError):
        return JsonResponse({'error': 'invalid data'}, status=400)

    try:
        exercise = Exercise.objects.select_related('lesson').get(pk=exercise_id)
    except Exercise.DoesNotExist:
        return JsonResponse({'error': 'not found'}, status=404)

    selected = request.POST.get('selected_option', '').strip().upper()

    ExerciseAnswer.objects.get_or_create(
        user=request.user,
        exercise=exercise,
        defaults={'selected_option': selected},
    )

    lesson = exercise.lesson
    lp = LessonProgress.objects.filter(user=request.user, lesson=lesson).first()
    newly_completed = False
    if lp:
        newly_completed = _try_complete_lesson(request.user, lp)

    total_ex = lesson.exercises.count()
    done_ex = ExerciseAnswer.objects.filter(user=request.user, exercise__lesson=lesson).count()

    return JsonResponse({
        'ok': True,
        'newly_completed': newly_completed,
        'pending_exercises': total_ex - done_ex,
    })


@login_required(login_url='accounts:login')
def update_progress(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'method not allowed'}, status=405)

    try:
        lesson_id   = int(request.POST.get('lesson_id', 0))
        current_time = int(float(request.POST.get('current_time', 0)))
        duration     = int(float(request.POST.get('duration', 0)))
    except (ValueError, TypeError):
        return JsonResponse({'error': 'invalid data'}, status=400)

    try:
        lesson = Lesson.objects.select_related('module').get(pk=lesson_id, is_active=True)
    except Lesson.DoesNotExist:
        return JsonResponse({'error': 'not found'}, status=404)

    lp, _ = LessonProgress.objects.get_or_create(user=request.user, lesson=lesson)

    lp.resume_position = current_time
    lp.watch_time_seconds = max(lp.watch_time_seconds, current_time)

    if not lp.video_watched and duration > 0 and current_time / duration >= 0.9:
        lp.video_watched = True

    lp.save()

    newly_completed = _try_complete_lesson(request.user, lp)

    pending_exercises = 0
    if lp.video_watched and not lp.completed:
        total_ex = lesson.exercises.count()
        done_ex = ExerciseAnswer.objects.filter(user=request.user, exercise__lesson=lesson).count()
        pending_exercises = total_ex - done_ex

    return JsonResponse({
        'completed': lp.completed,
        'newly_completed': newly_completed,
        'resume_position': lp.resume_position,
        'pending_exercises': pending_exercises,
    })

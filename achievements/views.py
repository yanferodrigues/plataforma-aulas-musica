from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from achievements.models import Achievement, UserAchievement


@login_required(login_url='accounts:login')
def achievements(request):
    user = request.user
    all_achievements = list(Achievement.objects.filter(is_active=True))
    unlocked_ids = set(
        UserAchievement.objects.filter(user=user).values_list('achievement_id', flat=True)
    )

    unlocked = [a for a in all_achievements if a.pk in unlocked_ids]
    locked = [a for a in all_achievements if a.pk not in unlocked_ids]

    total = len(all_achievements)
    unlocked_count = len(unlocked)
    pct = round(unlocked_count / total * 100) if total else 0

    context = {
        'unlocked': unlocked,
        'locked': locked,
        'total': total,
        'unlocked_count': unlocked_count,
        'pct': pct,
    }
    return render(request, 'achievements.html', context)

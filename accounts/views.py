from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from progress.models import LessonProgress, StudyStreak
from achievements.models import UserAchievement


def login_view(request):
    if request.user.is_authenticated:
        return redirect('courses:dashboard')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        try:
            username = User.objects.get(email=email).username
        except User.DoesNotExist:
            username = None

        user = authenticate(request, username=username, password=password) if username else None

        if user:
            login(request, user)
            return redirect(request.POST.get('next') or 'courses:dashboard')

        messages.error(request, 'E-mail ou senha inválidos.')

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('core:index')


def register(request):
    if request.user.is_authenticated:
        return redirect('courses:dashboard')

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if password != confirm_password:
            messages.error(request, 'As senhas não coincidem.')
            return render(request, 'register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'E-mail já cadastrado.')
            return render(request, 'register.html')

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        login(request, user)
        return redirect('courses:dashboard')

    return render(request, 'register.html')


def _profile_stats(user):
    total_seconds = (
        LessonProgress.objects.filter(user=user)
        .aggregate(total=Sum('watch_time_seconds'))['total'] or 0
    )
    completed_lessons = LessonProgress.objects.filter(user=user, completed=True).count()
    unlocked_count = UserAchievement.objects.filter(user=user).count()
    streak_obj = StudyStreak.objects.filter(user=user).first()
    streak = streak_obj.current_streak if streak_obj else 0
    return {
        'total_hours': total_seconds // 3600,
        'completed_lessons': completed_lessons,
        'unlocked_count': unlocked_count,
        'streak': streak,
    }


@login_required(login_url='accounts:login')
def profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name).strip()
        user.last_name = request.POST.get('last_name', user.last_name).strip()
        user.email = request.POST.get('email', user.email).strip()
        user.save()

        current_pw = request.POST.get('current_pw', '')
        new_pw = request.POST.get('new_pw', '')
        confirm_pw = request.POST.get('confirm_pw', '')

        if current_pw:
            if not user.check_password(current_pw):
                messages.error(request, 'Senha atual incorreta.')
                return redirect('accounts:profile')
            if new_pw != confirm_pw:
                messages.error(request, 'As novas senhas não coincidem.')
                return redirect('accounts:profile')
            user.set_password(new_pw)
            user.save()
            login(request, user)

        messages.success(request, 'Perfil atualizado com sucesso.')
        return redirect('accounts:profile')

    return render(request, 'profile.html', _profile_stats(request.user))


@login_required(login_url='accounts:login')
def settings_view(request):
    return render(request, 'settings.html')


def password_reset(request):
    return redirect('accounts:login')

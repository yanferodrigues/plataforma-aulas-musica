import os
import secrets
import logging
import urllib.parse
import requests as _requests

logger = logging.getLogger(__name__)

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.db.models import Sum
from progress.models import LessonProgress, StudyStreak
from achievements.models import UserAchievement
from .models import Notification

_GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')
_GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', '')


def send_notification(user, subject, message):
    """Envia email e salva notificação no banco para o usuário."""
    Notification.objects.create(user=user, subject=subject, message=message)
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
    except Exception as e:
        logger.error('Falha ao enviar email para %s: %s', user.email, e)


@login_required(login_url='accounts:login')
def notifications_api(request):
    qs = Notification.objects.filter(user=request.user)
    unread = qs.filter(is_read=False).count()
    if request.method == 'POST':
        qs.filter(is_read=False).update(is_read=True)
        return JsonResponse({'ok': True})
    data = [
        {
            'id': n.pk,
            'subject': n.subject,
            'message': n.message[:150] + ('…' if len(n.message) > 150 else ''),
            'is_read': n.is_read,
            'created_at': n.created_at.strftime('%d/%m/%Y %H:%M'),
        }
        for n in qs[:30]
    ]
    return JsonResponse({'notifications': data, 'unread': unread})


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

        send_notification(
            user=user,
            subject='Bem-vindo ao MUSILAB!',
            message=(
                f'Olá, {first_name or email}!\n\n'
                'Sua conta foi criada com sucesso. Bom estudo!\n\n'
                '— Equipe MUSILAB'
            ),
        )

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


# ── OAuth helpers ──────────────────────────────────────────────────────────────

def _callback_uri(request, provider):
    return request.build_absolute_uri(f'/accounts/{provider}/callback/')


def _get_or_create_social_user(email, first_name, last_name):
    try:
        return User.objects.get(email=email)
    except User.DoesNotExist:
        base = email.split('@')[0]
        username = base
        n = 1
        while User.objects.filter(username=username).exists():
            username = f'{base}{n}'
            n += 1
        return User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            # sem senha → conta social-only
        )


# ── Google OAuth ───────────────────────────────────────────────────────────────

def google_login(request):
    if not _GOOGLE_CLIENT_ID:
        messages.error(request, 'Login com Google não configurado.')
        return redirect('accounts:login')

    state = secrets.token_urlsafe(16)
    request.session['oauth_state'] = state

    params = {
        'client_id': _GOOGLE_CLIENT_ID,
        'redirect_uri': _callback_uri(request, 'google'),
        'scope': 'openid email profile',
        'response_type': 'code',
        'state': state,
        'access_type': 'online',
    }
    return redirect('https://accounts.google.com/o/oauth2/v2/auth?' + urllib.parse.urlencode(params))


def google_callback(request):
    stored_state = request.session.pop('oauth_state', None)
    if not stored_state or request.GET.get('state') != stored_state:
        messages.error(request, 'Falha na autenticação. Tente novamente.')
        return redirect('accounts:login')

    code = request.GET.get('code')
    if not code:
        messages.error(request, 'Autenticação com Google cancelada.')
        return redirect('accounts:login')

    token_resp = _requests.post('https://oauth2.googleapis.com/token', data={
        'code': code,
        'client_id': _GOOGLE_CLIENT_ID,
        'client_secret': _GOOGLE_CLIENT_SECRET,
        'redirect_uri': _callback_uri(request, 'google'),
        'grant_type': 'authorization_code',
    })
    access_token = token_resp.json().get('access_token')
    if not access_token:
        messages.error(request, 'Não foi possível autenticar com o Google.')
        return redirect('accounts:login')

    info = _requests.get(
        'https://www.googleapis.com/oauth2/v2/userinfo',
        headers={'Authorization': f'Bearer {access_token}'},
    ).json()

    email = info.get('email')
    if not email:
        messages.error(request, 'Não foi possível obter o e-mail da conta Google.')
        return redirect('accounts:login')

    user = _get_or_create_social_user(
        email=email,
        first_name=info.get('given_name', ''),
        last_name=info.get('family_name', ''),
    )
    login(request, user)
    return redirect('courses:dashboard')



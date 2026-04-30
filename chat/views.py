from datetime import datetime, timezone as dt_utc
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db.models import Q
from accounts.models import Notification, Profile
from .models import ChatMessage


def _user_role(user):
    if not user.is_superuser:
        return 'Aluno'
    try:
        role = user.profile.role
        return role if role else 'Professor'
    except Profile.DoesNotExist:
        return 'Professor'


def _user_photo(user):
    try:
        avatar = user.profile.avatar
        return avatar.url if avatar else None
    except Profile.DoesNotExist:
        return None


@login_required(login_url='accounts:login')
def chat_list(request):
    user = request.user

    all_students = None

    if user.is_superuser:
        # For search: all active non-superuser users
        all_students = User.objects.filter(is_active=True, is_superuser=False).order_by('first_name', 'last_name')

        # Conversations: only users with existing messages
        contacted_ids = ChatMessage.objects.filter(
            Q(sender=user) | Q(recipient=user)
        ).values_list('sender_id', 'recipient_id')
        other_ids = {uid for pair in contacted_ids for uid in pair if uid != user.pk}
        others = all_students.filter(pk__in=other_ids)
    else:
        others = User.objects.filter(is_active=True, is_superuser=True).order_by('first_name')

    conversations = []
    for other in others:
        last_msg = ChatMessage.objects.filter(
            Q(sender=user, recipient=other) | Q(sender=other, recipient=user)
        ).order_by('-created_at').first()
        unread = ChatMessage.objects.filter(sender=other, recipient=user, is_read=False).count()
        conversations.append({
            'user': other,
            'last_message': last_msg,
            'unread': unread,
            'photo': _user_photo(other),
            'role': _user_role(other),
        })

    conversations.sort(key=lambda x: (
        x['last_message'].created_at if x['last_message']
        else datetime.min.replace(tzinfo=dt_utc.utc)
    ), reverse=True)

    return render(request, 'chat_list.html', {
        'conversations': conversations,
        'all_students': all_students,
    })


@login_required(login_url='accounts:login')
def chat_room(request, user_id):
    other_user = get_object_or_404(User, pk=user_id, is_active=True)
    user = request.user

    if user == other_user:
        return redirect('chat:chat_list')
    if not user.is_superuser and not other_user.is_superuser:
        return redirect('chat:chat_list')

    # Mark incoming messages as read and remove their bell notifications
    ChatMessage.objects.filter(sender=other_user, recipient=user, is_read=False).update(is_read=True)
    sender_name = other_user.get_full_name() or other_user.username
    Notification.objects.filter(user=user, subject=f'Nova mensagem de {sender_name}').delete()

    messages_qs = ChatMessage.objects.filter(
        Q(sender=user, recipient=other_user) | Q(sender=other_user, recipient=user)
    ).order_by('created_at')

    return render(request, 'chat_room.html', {
        'other_user': other_user,
        'messages': messages_qs,
        'other_photo': _user_photo(other_user),
        'other_role': _user_role(other_user),
    })


@login_required(login_url='accounts:login')
def send_message(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    user = request.user
    recipient_id = request.POST.get('recipient_id')
    text = request.POST.get('text', '').strip()

    if not text or not recipient_id:
        return JsonResponse({'error': 'Missing fields'}, status=400)

    recipient = get_object_or_404(User, pk=recipient_id, is_active=True)

    if user == recipient:
        return JsonResponse({'error': 'Forbidden'}, status=403)
    if not user.is_superuser and not recipient.is_superuser:
        return JsonResponse({'error': 'Forbidden'}, status=403)

    msg = ChatMessage.objects.create(sender=user, recipient=recipient, text=text)

    sender_name = user.get_full_name() or user.username
    Notification.objects.create(
        user=recipient,
        subject=f'Nova mensagem de {sender_name}',
        message=text,
    )

    return JsonResponse({
        'id': msg.pk,
        'text': msg.text,
        'created_at': msg.created_at.strftime('%H:%M'),
    })


@login_required(login_url='accounts:login')
def poll_messages(request, user_id):
    other_user = get_object_or_404(User, pk=user_id, is_active=True)
    user = request.user
    after_id = int(request.GET.get('after', 0))

    ChatMessage.objects.filter(sender=other_user, recipient=user, is_read=False).update(is_read=True)
    sender_name = other_user.get_full_name() or other_user.username
    Notification.objects.filter(user=user, subject=f'Nova mensagem de {sender_name}').delete()

    new_msgs = ChatMessage.objects.filter(
        Q(sender=user, recipient=other_user) | Q(sender=other_user, recipient=user),
        pk__gt=after_id
    ).order_by('created_at')

    data = [{
        'id': m.pk,
        'text': m.text,
        'is_mine': m.sender_id == user.id,
        'created_at': m.created_at.strftime('%H:%M'),
    } for m in new_msgs]

    return JsonResponse({'messages': data})


@login_required(login_url='accounts:login')
def unread_count(request):
    count = ChatMessage.objects.filter(recipient=request.user, is_read=False).count()
    return JsonResponse({'unread': count})

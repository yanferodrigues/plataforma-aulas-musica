from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import NotificationSettings
from accounts.views import send_notification


class Command(BaseCommand):
    help = 'Envia lembretes de estudo para usuários que não estudaram hoje'

    def handle(self, *args, **options):
        today = timezone.localdate()
        settings_qs = NotificationSettings.objects.filter(
            study_reminders=True,
            user__is_active=True,
        ).select_related('user', 'user__studystreak')

        sent = 0
        for ns in settings_qs:
            user = ns.user
            try:
                streak = user.studystreak
                if streak.last_study_date == today:
                    continue
            except Exception:
                pass

            send_notification(
                user=user,
                subject='Hora de estudar! Não quebre sua sequência 🎵',
                message=(
                    f'Olá, {user.first_name or user.username}!\n\n'
                    'Você ainda não estudou hoje. Que tal assistir uma aula agora '
                    'e manter sua sequência ativa?\n\n'
                    '— Equipe MUSILAB'
                ),
            )
            sent += 1

        self.stdout.write(self.style.SUCCESS(f'Lembretes enviados: {sent}'))

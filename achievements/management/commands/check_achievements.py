from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from progress.views import _check_achievements


class Command(BaseCommand):
    help = 'Verifica e desbloqueia conquistas para todos os usuários com base no progresso existente'

    def add_arguments(self, parser):
        parser.add_argument('--user', type=int, help='ID de um usuário específico (opcional)')

    def handle(self, *args, **options):
        if options['user']:
            users = User.objects.filter(pk=options['user'])
        else:
            users = User.objects.filter(is_active=True)

        total = users.count()
        self.stdout.write(f'Verificando conquistas para {total} usuário(s)...')

        for user in users:
            _check_achievements(user)
            self.stdout.write(f'  ✓ {user.username}')

        self.stdout.write(self.style.SUCCESS('Concluído.'))

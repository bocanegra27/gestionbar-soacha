# ventas/management/commands/crear_superusuario.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import os

class Command(BaseCommand):
    help = 'Crea un superusuario a partir de variables de entorno'

    def handle(self, *args, **options):
        username = os.environ.get('ADMIN_USER')
        email = os.environ.get('ADMIN_EMAIL')
        password = os.environ.get('ADMIN_PASS')

        if not all([username, email, password]):
            self.stdout.write(self.style.ERROR('Faltan las variables de entorno ADMIN_USER, ADMIN_EMAIL o ADMIN_PASS.'))
            return

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username, email, password)
            self.stdout.write(self.style.SUCCESS(f'Superusuario "{username}" creado exitosamente.'))
        else:
            self.stdout.write(self.style.WARNING(f'El superusuario "{username}" ya existe.'))
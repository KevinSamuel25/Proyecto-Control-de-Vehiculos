from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Crea los roles (Operador/Consulta) y usuarios de prueba.'

    def handle(self, *args, **options):
        Group.objects.get_or_create(name='Operador')
        Group.objects.get_or_create(name='Consulta')

        usuarios = [
            ('admin', 'Admin123*', True, None),
            ('operador', 'Operador123*', False, 'Operador'),
            ('consulta', 'Consulta123*', False, 'Consulta'),
        ]

        for username, password, es_staff, grupo in usuarios:
            user, creado = User.objects.get_or_create(
                username=username,
                defaults={'is_staff': es_staff},
            )
            user.is_staff = es_staff
            user.set_password(password)
            user.save()
            user.groups.clear()
            if grupo:
                user.groups.add(Group.objects.get(name=grupo))
            estado = 'creado' if creado else 'actualizado'
            self.stdout.write(self.style.SUCCESS(
                f'Usuario {estado}: {username} (staff={es_staff}, grupo={grupo})'
            ))

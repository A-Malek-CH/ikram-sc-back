# users/management/commands/create_production_superuser.py

from django.core.management.base import BaseCommand
from users.models import User

class Command(BaseCommand):
    help = 'Creates a production superuser if one does not exist'

    def handle(self, *args, **options):
        email = 'admin@admin.com'
        password = 'malek1234'
        first_name = 'Admin'
        last_name = 'User'

        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f'Superuser with email {email} already exists.'))
            return

        try:
            User.objects.create_superuser(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully created superuser {email}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating superuser: {e}'))
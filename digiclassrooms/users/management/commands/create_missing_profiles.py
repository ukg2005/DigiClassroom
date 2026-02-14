from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import Profile

class Command(BaseCommand):
    help = 'Creates profiles for users that don\'t have one'

    def handle(self, *args, **kwargs):
        users_without_profile = []
        for user in User.objects.all():
            if not hasattr(user, 'profile'):
                users_without_profile.append(user)
                Profile.objects.create(user=user, is_teacher=False)
        
        if users_without_profile:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created profiles for {len(users_without_profile)} user(s)'
                )
            )
        else:
            self.stdout.write(self.style.SUCCESS('All users already have profiles'))

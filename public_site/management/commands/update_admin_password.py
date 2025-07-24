"""
Update admin user password from environment variable
"""

import os
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Update admin user password from ADMIN_PASSWORD environment variable"

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='srvo',
            help='Username to update password for (default: srvo)'
        )

    def handle(self, *args, **options):
        username = options['username']
        new_password = os.getenv("ADMIN_PASSWORD")
        
        if not new_password:
            self.stdout.write(
                self.style.ERROR(
                    "ADMIN_PASSWORD environment variable is required. "
                    "Please set it before running this command."
                )
            )
            return
        
        try:
            user = User.objects.get(username=username)
            user.set_password(new_password)
            user.save()
            
            self.stdout.write(
                self.style.SUCCESS(f"✓ Successfully updated password for user '{username}'")
            )
            
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"User '{username}' does not exist")
            )
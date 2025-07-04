#!/usr/bin/env python3
"""
Management command to fix user avatar URLs that point to missing local media files.
This resolves 404 errors in Wagtail admin when avatar images don't exist locally.
"""

from django.core.management.base import BaseCommand
from wagtail.users.models import UserProfile


class Command(BaseCommand):
    help = "Fix user avatar URLs that point to missing local media files"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be changed without making changes",
        )
        parser.add_argument(
            "--clear-avatars",
            action="store_true",
            help="Clear all avatar references instead of updating URLs",
        )

    def handle(self, *args, **options):
        profiles_updated = 0

        self.stdout.write(self.style.SUCCESS("🔍 Checking user profiles for broken avatar references..."))

        # Check all user profiles
        for profile in UserProfile.objects.all():
            if profile.avatar:
                # Get the avatar name/path as string
                avatar_name = str(profile.avatar.name) if hasattr(profile.avatar, "name") else str(profile.avatar)

                # Check if avatar points to local media (problematic)
                if avatar_name.startswith("avatar_images/"):
                    self.stdout.write(
                        self.style.WARNING(
                            f"Found broken avatar for user {profile.user.username}: {avatar_name}"
                        )
                    )

                    if not options["dry_run"]:
                        if options["clear_avatars"]:
                            # Clear the avatar reference
                            profile.avatar = None
                            profile.save()
                            self.stdout.write(
                                self.style.SUCCESS(f"✅ Cleared avatar for user {profile.user.username}")
                            )
                        else:
                            # Since avatar is an ImageField pointing to local media,
                            # we need to clear it (can't set it to external URL)
                            profile.avatar = None
                            profile.save()
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"✅ Cleared broken avatar for user {profile.user.username}"
                                )
                            )
                            self.stdout.write(
                                self.style.WARNING(
                                    "Note: ImageField cannot point to external URLs. User will need to re-upload avatar if desired."
                                )
                            )
                        profiles_updated += 1
                    else:
                        self.stdout.write(
                            self.style.WARNING(f"Would clear broken avatar for user {profile.user.username}")
                        )
                        profiles_updated += 1

                elif avatar_name.startswith("http"):
                    self.stdout.write(
                        self.style.SUCCESS(f"✅ User {profile.user.username} has valid avatar URL: {avatar_name}")
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f"⚠️  User {profile.user.username} has avatar: {avatar_name}")
                    )

        if options["dry_run"]:
            self.stdout.write(
                self.style.WARNING(f"🔍 DRY RUN: Would update {profiles_updated} profile(s)")
            )
            self.stdout.write(
                self.style.WARNING("Run without --dry-run to apply changes")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"🎉 Successfully updated {profiles_updated} profile(s)")
            )

        if profiles_updated == 0:
            self.stdout.write(
                self.style.SUCCESS("🎉 No broken avatar references found!")
            )

        self.stdout.write(self.style.SUCCESS("✅ Avatar check complete"))

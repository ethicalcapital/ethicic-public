"""
Fix Wagtail image permissions and collections
"""

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from wagtail.core.models import Collection
from wagtail.images.models import Image


class Command(BaseCommand):
    help = "Fix Wagtail image permissions and collections"

    def handle(self, *args, **options):
        self.stdout.write("🔧 Fixing Wagtail image permissions and collections...")

        try:
            # Ensure root collection exists
            root_collection = Collection.get_first_root_node()
            if not root_collection:
                self.stdout.write("📁 Creating root collection...")
                Collection.add_root(name="Root", slug="root")
                root_collection = Collection.get_first_root_node()

            self.stdout.write(f"✅ Root collection exists: {root_collection.name}")

            # Get or create Images collection
            images_collection, created = Collection.objects.get_or_create(
                name="Images",
                defaults={
                    "slug": "images",
                },
            )

            if created:
                # Make it a child of root if it doesn't have a parent
                if not images_collection.get_parent():
                    root_collection.add_child(instance=images_collection)
                self.stdout.write("📸 Created Images collection")
            else:
                self.stdout.write("✅ Images collection exists")

            # Check image content type and permissions
            image_ct = ContentType.objects.get_for_model(Image)
            permissions = Permission.objects.filter(content_type=image_ct)

            self.stdout.write(f"📋 Found {permissions.count()} image permissions:")
            for perm in permissions:
                self.stdout.write(f"  - {perm.codename}: {perm.name}")

            # Get all groups and check their permissions
            groups = Group.objects.all()
            self.stdout.write(f"👥 Found {groups.count()} user groups")

            for group in groups:
                image_perms = group.permissions.filter(content_type=image_ct)
                if image_perms.exists():
                    self.stdout.write(
                        f"  Group '{group.name}' has {image_perms.count()} image permissions"
                    )
                else:
                    self.stdout.write(
                        f"  Group '{group.name}' has NO image permissions"
                    )

            # Check if any users exist
            from django.contrib.auth import get_user_model

            User = get_user_model()
            users = User.objects.all()
            self.stdout.write(f"👤 Found {users.count()} users")

            if users.count() > 0:
                for user in users:
                    if user.is_superuser:
                        self.stdout.write(f"  User '{user.username}' is superuser ✅")
                    else:
                        user_groups = user.groups.all()
                        self.stdout.write(
                            f"  User '{user.username}' is in {user_groups.count()} groups"
                        )

            self.stdout.write("✅ Image permissions and collections check complete!")

        except Exception as e:
            self.stdout.write(f"❌ Error: {str(e)}")
            import traceback

            self.stdout.write(traceback.format_exc())

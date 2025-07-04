from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from wagtail.documents.models import Document
from wagtail.images.models import Image
from wagtail.models import (
    Collection,
    GroupCollectionPermission,
    GroupPagePermission,
    Page,
)


class Command(BaseCommand):
    help = "Fix Wagtail permissions to ensure pages are editable"

    def handle(self, *args, **options):
        self.stdout.write("=== Fixing Wagtail Permissions ===")

        # Get or create editors group
        editors_group, created = Group.objects.get_or_create(name="Editors")
        if created:
            self.stdout.write(self.style.SUCCESS("Created 'Editors' group"))

        # Get or create moderators group
        moderators_group, created = Group.objects.get_or_create(name="Moderators")
        if created:
            self.stdout.write(self.style.SUCCESS("Created 'Moderators' group"))

        # Add Wagtail permissions to groups
        wagtail_perms = Permission.objects.filter(
            content_type__app_label__in=[
                "wagtailcore",
                "wagtailadmin",
                "wagtailimages",
                "wagtaildocs",
                "taggit",
            ]
        )

        # Give editors basic permissions
        editor_perms = wagtail_perms.filter(
            codename__in=[
                "add_page",
                "change_page",
                "publish_page",
                "add_image",
                "change_image",
                "add_document",
                "change_document",
                "add_tag",
                "change_tag",
            ]
        )
        editors_group.permissions.set(editor_perms)
        self.stdout.write(f"Added {editor_perms.count()} permissions to Editors group")

        # Give moderators more permissions
        moderators_group.permissions.set(wagtail_perms)
        self.stdout.write(
            f"Added {wagtail_perms.count()} permissions to Moderators group"
        )

        # Setup page permissions
        Page.objects.get(id=1)
        homepage = Page.objects.filter(id=3).first()

        if homepage:
            # Give editors permission to edit under homepage
            # Get the permission objects
            add_perm = Permission.objects.get(
                content_type__app_label="wagtailcore", codename="add_page"
            )
            edit_perm = Permission.objects.get(
                content_type__app_label="wagtailcore", codename="change_page"
            )
            publish_perm = Permission.objects.get(
                content_type__app_label="wagtailcore", codename="publish_page"
            )

            GroupPagePermission.objects.get_or_create(
                group=editors_group,
                page=homepage,
                permission=add_perm,
            )
            GroupPagePermission.objects.get_or_create(
                group=editors_group,
                page=homepage,
                permission=edit_perm,
            )
            GroupPagePermission.objects.get_or_create(
                group=editors_group,
                page=homepage,
                permission=publish_perm,
            )
            self.stdout.write(self.style.SUCCESS("Added page permissions for Editors"))

        # Setup collection permissions
        root_collection = Collection.objects.get(name="Root")

        # Image permissions
        image_content_type = ContentType.objects.get_for_model(Image)
        image_perms = Permission.objects.filter(content_type=image_content_type)

        for perm in image_perms:
            GroupCollectionPermission.objects.get_or_create(
                group=editors_group, collection=root_collection, permission=perm
            )

        # Document permissions
        doc_content_type = ContentType.objects.get_for_model(Document)
        doc_perms = Permission.objects.filter(content_type=doc_content_type)

        for perm in doc_perms:
            GroupCollectionPermission.objects.get_or_create(
                group=editors_group, collection=root_collection, permission=perm
            )

        self.stdout.write(
            self.style.SUCCESS("Added collection permissions for Editors")
        )

        # Update all staff users
        staff_users = User.objects.filter(is_staff=True, is_superuser=False)
        for user in staff_users:
            user.groups.add(editors_group)
            self.stdout.write(f"Added {user.username} to Editors group")

        # Grant access to Wagtail admin
        access_admin_perm = Permission.objects.filter(
            content_type__app_label="wagtailadmin", codename="access_admin"
        ).first()

        if access_admin_perm:
            editors_group.permissions.add(access_admin_perm)
            moderators_group.permissions.add(access_admin_perm)
            self.stdout.write(
                self.style.SUCCESS("Added Wagtail admin access permission")
            )

        # Add public_site permissions
        public_site_perms = Permission.objects.filter(
            content_type__app_label="public_site"
        )
        editors_group.permissions.add(*public_site_perms)
        self.stdout.write(
            f"Added {public_site_perms.count()} public_site permissions to Editors"
        )

        self.stdout.write(
            self.style.SUCCESS("\n✅ Wagtail permissions fixed successfully!")
        )
        self.stdout.write("\nStaff users can now:")
        self.stdout.write("- Access Wagtail admin at /cms-admin/")
        self.stdout.write("- Edit pages under 'Ethical Capital | Investment Advisory'")
        self.stdout.write("- Upload and manage images and documents")
        self.stdout.write("- Create and publish pages")

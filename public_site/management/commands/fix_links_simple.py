"""
Simple management command to fix remaining broken link references using database queries
"""
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Fix remaining broken link references using direct SQL updates"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be changed without making changes",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        if dry_run:
            self.stdout.write("DRY RUN MODE - No changes will be made\n")

        # URL mappings
        url_mappings = [
            ("https://app.precisefp.com/w/ixj9du", "/onboarding/"),
            ("https://app.precisefp.com/w/bi4ccx", "/onboarding/"),
            ("/performance/", "/strategies/"),
        ]

        with connection.cursor() as cursor:
            for old_url, new_url in url_mappings:
                self.stdout.write(f"Searching for: {old_url}")

                # Check blog posts
                cursor.execute(
                    """
                    SELECT bp.page_ptr_id, p.title, bp.body
                    FROM public_site_blogpost bp
                    JOIN wagtailcore_page p ON bp.page_ptr_id = p.id
                    WHERE bp.body LIKE %s
                """,
                    [f"%{old_url}%"],
                )

                results = cursor.fetchall()
                for post_id, title, body in results:
                    self.stdout.write(f"  Found in blog post: {title} (ID: {post_id})")

                    if not dry_run:
                        # Update the blog post
                        new_body = body.replace(old_url, new_url)
                        cursor.execute(
                            """
                            UPDATE public_site_blogpost
                            SET body = %s
                            WHERE page_ptr_id = %s
                        """,
                            [new_body, post_id],
                        )
                        self.stdout.write(f"  ✅ Updated blog post: {title}")

                # Skip other pages for now - focus on blog posts only

        if dry_run:
            self.stdout.write("\nDRY RUN COMPLETE")
        else:
            self.stdout.write("\nUPDATES COMPLETE")

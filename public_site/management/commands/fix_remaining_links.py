"""
Management command to fix remaining broken link references
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from wagtail.models import Page

from public_site.models import BlogPost


class Command(BaseCommand):
    help = "Fix remaining broken link references (precisefp and performance)"

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

        changes_made = 0

        # URL mappings
        url_mappings = {
            "https://app.precisefp.com/w/ixj9du": "/onboarding/",
            "https://app.precisefp.com/w/bi4ccx": "/onboarding/",
            "/performance/": "/strategies/",
        }

        with transaction.atomic():
            # Search blog posts
            blog_posts = BlogPost.objects.all()

            for post in blog_posts:
                if hasattr(post, "body") and post.body:
                    body_text = str(post.body)
                    original_text = body_text

                    # Apply URL mappings
                    for old_url, new_url in url_mappings.items():
                        if old_url in body_text:
                            body_text = body_text.replace(old_url, new_url)
                            self.stdout.write(
                                f"Updated {old_url} -> {new_url} in: {post.title}"
                            )
                            changes_made += 1

                    # Save if changes were made
                    if body_text != original_text and not dry_run:
                        # Update the body field with new content
                        import json

                        # Get the raw StreamField data
                        if hasattr(post.body, "raw_text"):
                            body_data = json.loads(post.body.raw_text)
                        else:
                            body_data = json.loads(str(post.body.raw_data))

                        # Update text in blocks
                        def update_blocks(blocks):
                            for block in blocks:
                                if (
                                    block.get("type") == "paragraph"
                                    and "value" in block
                                ) or (
                                    block.get("type") == "rich_text"
                                    and "value" in block
                                ):
                                    original_value = block["value"]
                                    new_value = original_value
                                    for old_url, new_url in url_mappings.items():
                                        new_value = new_value.replace(old_url, new_url)
                                    block["value"] = new_value

                        update_blocks(body_data)

                        # Create new StreamField with updated data
                        from wagtail.fields import StreamValue

                        post.body = StreamValue(
                            post.body.stream_block, body_data, is_lazy=True
                        )
                        post.save()

            # Search other page types
            other_pages = Page.objects.live().exclude(blogpost__isnull=False)

            for page in other_pages:
                if hasattr(page, "body") and page.body:
                    body_text = str(page.body)
                    original_text = body_text

                    # Apply URL mappings
                    for old_url, new_url in url_mappings.items():
                        if old_url in body_text:
                            body_text = body_text.replace(old_url, new_url)
                            self.stdout.write(
                                f"Updated {old_url} -> {new_url} in page: {page.title}"
                            )
                            changes_made += 1

                    # Save if changes were made
                    if body_text != original_text and not dry_run:
                        # Similar update logic for pages
                        import json

                        try:
                            body_data = json.loads(page.body.raw_text)

                            def update_blocks(blocks):
                                for block in blocks:
                                    if (
                                        block.get("type") == "paragraph"
                                        and "value" in block
                                    ) or (
                                        block.get("type") == "rich_text"
                                        and "value" in block
                                    ):
                                        original_value = block["value"]
                                        new_value = original_value
                                        for old_url, new_url in url_mappings.items():
                                            new_value = new_value.replace(
                                                old_url, new_url
                                            )
                                        block["value"] = new_value

                            update_blocks(body_data)
                            page.body = json.dumps(body_data)
                            page.save()
                        except Exception as e:
                            self.stdout.write(
                                f"Could not update page {page.title} - complex body structure: {e}"
                            )

        if dry_run:
            self.stdout.write(f"\nDRY RUN: Would make {changes_made} changes")
        else:
            self.stdout.write(f"\nCompleted! Made {changes_made} changes")

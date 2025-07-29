"""
Management command to find specific references in content
"""

from django.core.management.base import BaseCommand
from wagtail.models import Page

from public_site.models import BlogPost


class Command(BaseCommand):
    help = "Find references to specific URLs in content"

    def handle(self, *args, **options):
        self.stdout.write("Searching for precisefp and /performance/ references...\n")

        # Search blog posts
        blog_posts = BlogPost.objects.all()

        for post in blog_posts:
            if hasattr(post, "body") and post.body:
                body_text = str(post.body)

                if "precisefp" in body_text.lower():
                    self.stdout.write(
                        f"PreciseFP found in: {post.title} (ID: {post.id})"
                    )
                    self.stdout.write(f"URL: {post.get_url()}")

                if "/performance/" in body_text:
                    self.stdout.write(
                        f"Performance ref found in: {post.title} (ID: {post.id})"
                    )
                    self.stdout.write(f"URL: {post.get_url()}")

        # Search other page types
        other_pages = Page.objects.live().exclude(blogpost__isnull=False)

        for page in other_pages:
            if hasattr(page, "body") and page.body:
                body_text = str(page.body)

                if "precisefp" in body_text.lower():
                    self.stdout.write(
                        f"PreciseFP found in page: {page.title} (ID: {page.id})"
                    )
                    self.stdout.write(f"URL: {page.get_url()}")

                if "/performance/" in body_text:
                    self.stdout.write(
                        f"Performance ref found in page: {page.title} (ID: {page.id})"
                    )
                    self.stdout.write(f"URL: {page.get_url()}")

        self.stdout.write("\nSearch complete.")

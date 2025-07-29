"""
Management command to update all investvegan.org references in blog post content.

This command systematically replaces broken investvegan.org URLs with appropriate
ethicic.com equivalents or removes them if no equivalent exists.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from public_site.models import BlogPost


class Command(BaseCommand):
    help = "Update all investvegan.org references in blog post content to ethicic.com equivalents"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what changes would be made without applying them",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Show detailed output for each change",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        verbose = options["verbose"]

        # URL mapping configuration
        url_mappings = {
            # Page references that have direct equivalents
            "https://investvegan.org/contact-us/": "https://ethicic.com/contact/",
            "https://investvegan.org/our-process/": "https://ethicic.com/process/",
            "https://investvegan.org/support/": "https://ethicic.com/faq/",
            "https://investvegan.org/stock-market-performance-what-should-you-expect/": "https://ethicic.com/blog/stock-market-performance-what-should-you-expect/",
            "https://investvegan.org/why-we-own-farmer-mac/": "https://ethicic.com/blog/why-we-own-farmer-mac/",
            # Current URLs found in the database
            "https://investvegan.org/strategies/": "https://ethicic.com/strategies/",
            "https://investvegan.org/gimmewebinar": "https://ethicic.com/contact/",  # Redirect webinar requests to contact
        }

        # Email mapping configuration
        email_mappings = {
            "sloane@investvegan.org": "sloane@ethicic.com",
        }

        # Image URLs - these need special handling since they're hosted on the old site
        # For now, we'll document them but leave them as-is since they may need
        # to be re-uploaded to the new site's media system
        image_urls_found = [
            "https://investvegan.org/wp-content/uploads/2022/03/world-population-with-and-without-fertilizer-1024x723.png",
            "https://investvegan.org/wp-content/uploads/2022/03/coefficient-of-variation-cv-in-per-capita-caloric-intake-1-1024x723.png",
            "https://investvegan.org/wp-content/uploads/2023/05/image-1-1024x576.png",
            "https://investvegan.org/wp-content/uploads/2023/05/image-2.png",
        ]

        changes_made = []
        posts_updated = 0

        # Find all posts with investvegan.org references
        all_posts = BlogPost.objects.all()
        posts_with_references = []

        for post in all_posts:
            content_text = str(post.content) if post.content else ""
            body_text = str(post.body) if post.body else ""

            if "investvegan.org" in content_text or "investvegan.org" in body_text:
                posts_with_references.append(post)

        self.stdout.write(
            f"Found {len(posts_with_references)} posts with investvegan.org references"
        )

        if not posts_with_references:
            self.stdout.write(
                self.style.SUCCESS("No posts found with investvegan.org references.")
            )
            return

        with transaction.atomic():
            for post in posts_with_references:
                post_changes = []
                original_content = str(post.content)
                original_body = str(post.body)

                updated_content = original_content
                updated_body = original_body

                # Apply URL mappings to both content and body
                for old_url, new_url in url_mappings.items():
                    # Update content field
                    if old_url in updated_content:
                        updated_content = updated_content.replace(old_url, new_url)
                        post_changes.append(f"Content: {old_url} → {new_url}")

                    # Update body field
                    if old_url in updated_body:
                        updated_body = updated_body.replace(old_url, new_url)
                        post_changes.append(f"Body: {old_url} → {new_url}")

                # Apply email mappings to both content and body
                for old_email, new_email in email_mappings.items():
                    # Update content field
                    if old_email in updated_content:
                        updated_content = updated_content.replace(old_email, new_email)
                        post_changes.append(f"Content: {old_email} → {new_email}")

                    # Update body field
                    if old_email in updated_body:
                        updated_body = updated_body.replace(old_email, new_email)
                        post_changes.append(f"Body: {old_email} → {new_email}")

                # Check for image URLs and report them
                for image_url in image_urls_found:
                    if image_url in updated_content or image_url in updated_body:
                        post_changes.append(
                            f"IMAGE FOUND (needs manual review): {image_url}"
                        )

                # Apply changes if any were made
                if post_changes:
                    posts_updated += 1

                    if verbose or dry_run:
                        self.stdout.write(
                            f"\n--- Post: {post.title} (ID: {post.id}) ---"
                        )
                        for change in post_changes:
                            self.stdout.write(f"  {change}")

                    if not dry_run:
                        # Save the updated content
                        post.content = updated_content
                        post.body = updated_body
                        post.save()

                        # Track changes for summary
                        changes_made.extend(
                            [
                                {
                                    "post_id": post.id,
                                    "post_title": post.title,
                                    "post_slug": post.slug,
                                    "changes": post_changes,
                                }
                            ]
                        )

        # Summary output
        if dry_run:
            self.stdout.write(f"\n{self.style.WARNING('DRY RUN COMPLETE')}")
            self.stdout.write(f"Would update {posts_updated} posts")
        else:
            self.stdout.write(f"\n{self.style.SUCCESS('UPDATE COMPLETE')}")
            self.stdout.write(f"Updated {posts_updated} posts")

        # Report image URLs that need manual attention
        if image_urls_found:
            self.stdout.write(
                f"\n{self.style.WARNING('IMAGE URLs REQUIRING MANUAL REVIEW:')}"
            )
            for img_url in image_urls_found:
                self.stdout.write(f"  {img_url}")
            self.stdout.write(
                "These images may need to be re-uploaded to ethicic.com's media system."
            )

        # Detailed summary
        if changes_made and verbose:
            self.stdout.write(f"\n{self.style.SUCCESS('DETAILED CHANGES SUMMARY:')}")
            for change_record in changes_made:
                self.stdout.write(
                    f"\nPost: {change_record['post_title']} ({change_record['post_slug']})"
                )
                for change in change_record["changes"]:
                    self.stdout.write(f"  ✓ {change}")

#!/usr/bin/env python3
"""
Management command to update all blog posts with calculated reading times.
This fixes the issue where all posts have the same manual reading time.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from public_site.models import BlogPost


class Command(BaseCommand):
    help = "Update all blog posts with automatically calculated reading times"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be updated without making changes",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force update even if reading_time is already set",
        )

    def handle(self, *args, **options):
        self.stdout.write("🔍 UPDATING BLOG POST READING TIMES")
        self.stdout.write("=" * 50)

        # Get all blog posts
        posts = BlogPost.objects.live().public().order_by("-first_published_at")
        total_posts = posts.count()

        if total_posts == 0:
            self.stdout.write(
                self.style.WARNING("No blog posts found.")
            )
            return

        self.stdout.write(f"Found {total_posts} blog posts to process")

        updated_count = 0
        skipped_count = 0

        with transaction.atomic():
            for i, post in enumerate(posts, 1):
                # Calculate new reading time
                calculated_time = post.calculate_reading_time()
                current_time = post.reading_time

                # Determine if we should update
                should_update = (
                    options["force"] or 
                    current_time is None or 
                    current_time == 5  # Update the common default value
                )

                if should_update:
                    if options["dry_run"]:
                        self.stdout.write(
                            f"[{i:2d}/{total_posts}] WOULD UPDATE: {post.title[:40]:<40} | "
                            f"{current_time} → {calculated_time} min"
                        )
                    else:
                        # Update reading time
                        post.reading_time = calculated_time
                        post.save(update_fields=['reading_time'])
                        
                        self.stdout.write(
                            f"[{i:2d}/{total_posts}] ✅ UPDATED: {post.title[:40]:<40} | "
                            f"{current_time} → {calculated_time} min"
                        )
                    updated_count += 1
                else:
                    self.stdout.write(
                        f"[{i:2d}/{total_posts}] ⏭️  SKIPPED: {post.title[:40]:<40} | "
                        f"keeping {current_time} min (use --force to override)"
                    )
                    skipped_count += 1

        # Summary
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("SUMMARY")
        self.stdout.write("=" * 50)

        if options["dry_run"]:
            self.stdout.write(
                self.style.WARNING(f"DRY RUN: Would update {updated_count} posts")
            )
            self.stdout.write(f"Would skip {skipped_count} posts")
            self.stdout.write("\nRun without --dry-run to apply changes")
        else:
            self.stdout.write(
                self.style.SUCCESS(f"✅ Updated {updated_count} blog posts")
            )
            self.stdout.write(f"⏭️  Skipped {skipped_count} posts")

        self.stdout.write("\n💡 NOTES:")
        self.stdout.write("- New posts will automatically calculate reading time")
        self.stdout.write("- Existing posts with custom times were preserved (use --force to override)")
        self.stdout.write("- Reading time is based on 200 words per minute")
        self.stdout.write("- Minimum reading time is 1 minute")
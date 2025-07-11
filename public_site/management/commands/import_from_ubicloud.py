"""
Management command to import public site data from Ubicloud database
"""

from django.core.management.base import BaseCommand
from django.db import connections, transaction
from wagtail.models import Page, Site

from public_site.models import BlogPost, HomePage, MediaItem, SupportTicket


class Command(BaseCommand):
    help = "Import public site data from Ubicloud database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--skip-pages", action="store_true", help="Skip importing Wagtail pages"
        )
        parser.add_argument(
            "--skip-media", action="store_true", help="Skip importing media items"
        )
        parser.add_argument(
            "--skip-tickets", action="store_true", help="Skip importing support tickets"
        )

    def handle(self, *args, **options):
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("Data Import from Ubicloud")
        self.stdout.write("=" * 60)

        # Check if Ubicloud database is configured
        if "ubicloud" not in connections:
            self.stdout.write(
                self.style.WARNING("\n⚠️  UBI_DATABASE_URL not configured")
            )
            self.stdout.write("   Skipping data import - no source database")
            self.stdout.write("=" * 60 + "\n")
            return  # Exit gracefully

        # Show connection info (sanitized)
        conn_settings = connections["ubicloud"].settings_dict
        self.stdout.write("\nConnection settings:")
        self.stdout.write(f"  Host: {conn_settings.get('HOST', 'N/A')}")
        self.stdout.write(f"  Port: {conn_settings.get('PORT', 'N/A')}")
        self.stdout.write(f"  Database: {conn_settings.get('NAME', 'N/A')}")
        self.stdout.write(
            f"  SSL Mode: {conn_settings.get('OPTIONS', {}).get('sslmode', 'N/A')}"
        )

        # Test Ubicloud connection
        self.stdout.write("\nTesting connection...")
        try:
            with connections["ubicloud"].cursor() as cursor:
                cursor.execute("SELECT version()")
                version = cursor.fetchone()[0]
                self.stdout.write(
                    self.style.SUCCESS("✅ Connected to Ubicloud database")
                )
                self.stdout.write(f"   PostgreSQL {version.split(',')[0]}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n❌ Connection failed: {e}"))
            self.stdout.write("   Check your UBI_DATABASE_URL and network connectivity")
            self.stdout.write("   Continuing without data import")
            self.stdout.write("=" * 60 + "\n")
            return  # Exit gracefully

        # Import data
        with transaction.atomic():
            if not options["skip_pages"]:
                self._import_pages()

            if not options["skip_media"]:
                self._import_media_items()

            if not options["skip_tickets"]:
                self._import_support_tickets()

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("✅ Data import completed successfully!"))
        self.stdout.write("=" * 60 + "\n")

    def _import_pages(self):
        """Import Wagtail pages from Ubicloud"""
        self.stdout.write("Importing pages...")

        try:
            # Get data from Ubicloud
            with connections["ubicloud"].cursor() as cursor:
                # Import HomePage
                cursor.execute(
                    """
                    SELECT id, title, slug, hero_title, hero_subtitle, body
                    FROM public_site_homepage
                    WHERE live = true
                    LIMIT 1
                """
                )

                home_data = cursor.fetchone()
                if home_data:
                    # Check if we already have a homepage
                    if not HomePage.objects.exists():
                        root = Page.objects.get(id=1)
                        home = HomePage(
                            title=home_data[1],
                            slug=home_data[2],
                            hero_title=home_data[3] or "",
                            hero_subtitle=home_data[4] or "",
                            body=home_data[5] or "",
                        )
                        root.add_child(instance=home)

                        # Update site
                        Site.objects.all().delete()
                        Site.objects.create(
                            hostname="ethicic-public-svoo7.kinsta.app",
                            root_page=home,
                            is_default_site=True,
                        )
                        self.stdout.write(self.style.SUCCESS("✓ Imported HomePage"))
                    else:
                        # Update existing homepage
                        home = HomePage.objects.first()
                        home.hero_title = home_data[3] or home.hero_title
                        home.hero_subtitle = home_data[4] or home.hero_subtitle
                        home.body = home_data[5] or home.body
                        home.save()
                        self.stdout.write(
                            self.style.SUCCESS("✓ Updated existing HomePage")
                        )

                # Import BlogPosts
                cursor.execute(
                    """
                    SELECT COUNT(*) FROM public_site_blogpost
                    WHERE live = true
                """
                )
                blog_count = cursor.fetchone()[0]

                if blog_count > 0:
                    cursor.execute(
                        """
                        SELECT id, title, slug, subtitle, date, summary,
                               author, body, updated_at
                        FROM public_site_blogpost
                        WHERE live = true
                        ORDER BY date DESC
                    """
                    )

                    blog_posts = cursor.fetchall()
                    imported = 0

                    for post_data in blog_posts:
                        # Check if post already exists by slug
                        if not BlogPost.objects.filter(slug=post_data[2]).exists():
                            # Find parent page (blog index or home)
                            parent = HomePage.objects.first()
                            if parent:
                                blog = BlogPost(
                                    title=post_data[1],
                                    slug=post_data[2],
                                    subtitle=post_data[3] or "",
                                    date=post_data[4],
                                    summary=post_data[5] or "",
                                    author=post_data[6] or "Ethical Capital",
                                    body=post_data[7] or "",
                                )
                                parent.add_child(instance=blog)
                                imported += 1

                    self.stdout.write(
                        self.style.SUCCESS(f"✓ Imported {imported} blog posts")
                    )

        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Page import partially failed: {e}"))

    def _import_media_items(self):
        """Import media items from Ubicloud"""
        self.stdout.write("Importing media items...")

        try:
            with connections["ubicloud"].cursor() as cursor:
                cursor.execute(
                    """
                    SELECT title, publication, url, date, excerpt,
                           featured, created_at, updated_at
                    FROM public_site_mediaitem
                    ORDER BY date DESC
                """
                )

                media_items = cursor.fetchall()
                imported = 0

                for item in media_items:
                    # Check if already exists
                    if not MediaItem.objects.filter(
                        title=item[0], publication=item[1]
                    ).exists():
                        MediaItem.objects.create(
                            title=item[0],
                            publication=item[1],
                            url=item[2],
                            date=item[3],
                            excerpt=item[4] or "",
                            featured=item[5],
                            created_at=item[6],
                            updated_at=item[7],
                        )
                        imported += 1

                self.stdout.write(
                    self.style.SUCCESS(f"✓ Imported {imported} media items")
                )

        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Media import failed: {e}"))

    def _import_support_tickets(self):
        """Import support tickets from Ubicloud"""
        self.stdout.write("Importing support tickets...")

        try:
            with connections["ubicloud"].cursor() as cursor:
                cursor.execute(
                    """
                    SELECT ticket_type, name, email, company, subject,
                           message, status, priority, created_at,
                           updated_at, resolved_at, notes
                    FROM public_site_supportticket
                    WHERE created_at > NOW() - INTERVAL '90 days'
                    ORDER BY created_at DESC
                """
                )

                tickets = cursor.fetchall()
                imported = 0

                for ticket in tickets:
                    # Check if already exists
                    if not SupportTicket.objects.filter(
                        email=ticket[2], subject=ticket[4], created_at=ticket[8]
                    ).exists():
                        SupportTicket.objects.create(
                            ticket_type=ticket[0],
                            name=ticket[1],
                            email=ticket[2],
                            company=ticket[3],
                            subject=ticket[4],
                            message=ticket[5],
                            status=ticket[6],
                            priority=ticket[7],
                            created_at=ticket[8],
                            updated_at=ticket[9],
                            resolved_at=ticket[10],
                            notes=ticket[11] or "",
                        )
                        imported += 1

                self.stdout.write(
                    self.style.SUCCESS(f"✓ Imported {imported} support tickets")
                )

        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Support ticket import failed: {e}"))

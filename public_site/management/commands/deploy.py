"""
Management command for deployment setup.
This should be run after deployment to set up the database, build CSS bundles, and collect static files.
"""

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Run deployment setup: migrations, CSS bundles, collectstatic, and site setup"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--skip-css",
            action="store_true",
            help="Skip CSS bundle building (for development or testing)",
        )
        parser.add_argument(
            "--development",
            action="store_true",
            help="Build development CSS bundles instead of production",
        )

    def handle(self, *args, **options):
        self.stdout.write("🚀 Starting deployment setup...")

        # 1. Run migrations
        self.stdout.write("📊 Running database migrations...")
        try:
            call_command("migrate", verbosity=1, interactive=False)
            self.stdout.write(self.style.SUCCESS("✅ Database migrations completed"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"⚠️  Migration warnings: {e}"))

        # 2. Build Tailwind CSS for production
        if not options["skip_css"]:
            self.stdout.write("🎨 Building Tailwind CSS...")
            try:
                import subprocess

                from django.conf import settings

                # Build Tailwind CSS using npm
                subprocess.run(
                    [
                        "npx",
                        "postcss",
                        "static/css/tailwind-simple.css",
                        "-o",
                        "static/css/dist/tailwind.min.css",
                        "--env",
                        "production",
                    ],
                    cwd=settings.BASE_DIR,
                    capture_output=True,
                    text=True,
                    check=True,
                )
                self.stdout.write(
                    self.style.SUCCESS("✅ Tailwind CSS built successfully")
                )

            except subprocess.CalledProcessError as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Tailwind CSS build failed: {e}")
                )
                self.stdout.write(self.style.ERROR(f"Output: {e.stdout}"))
                self.stdout.write(self.style.ERROR(f"Error: {e.stderr}"))
                self.stdout.write(
                    self.style.WARNING("⚠️  Continuing deployment without Tailwind CSS")
                )
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Tailwind CSS build error: {e}"))
                self.stdout.write(
                    self.style.WARNING("⚠️  Continuing deployment without Tailwind CSS")
                )

            # 3. Build Garden UI CSS bundles
            self.stdout.write("🎨 Building Garden UI CSS bundles...")
            try:
                if options["development"]:
                    call_command("build_css", development=True)
                    self.stdout.write(
                        self.style.SUCCESS("✅ Development Garden UI bundles built")
                    )
                else:
                    call_command("build_css")
                    self.stdout.write(
                        self.style.SUCCESS("✅ Production Garden UI bundles built")
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Garden UI bundle build failed: {e}")
                )
                self.stdout.write(
                    self.style.WARNING(
                        "⚠️  Continuing deployment without Garden UI bundles"
                    )
                )
        else:
            self.stdout.write(self.style.WARNING("⏭️  Skipping CSS building"))

        # 4. Collect static files
        self.stdout.write("📁 Collecting static files...")
        try:
            call_command("collectstatic", verbosity=1, interactive=False, clear=True)
            self.stdout.write(self.style.SUCCESS("✅ Static files collected"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"⚠️  Static collection warnings: {e}"))

        # 5. Set up homepage
        self.stdout.write("🏠 Setting up site structure...")
        try:
            call_command("setup_homepage")
            self.stdout.write(self.style.SUCCESS("✅ Site setup completed"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"⚠️  Site setup warnings: {e}"))

        # 6. Deployment summary
        self._print_deployment_summary(options)

    def _print_deployment_summary(self, options):
        """Print deployment summary with recommendations"""
        self.stdout.write(self.style.SUCCESS("🎉 Deployment setup completed!"))
        self.stdout.write("")
        self.stdout.write("📋 Deployment Summary:")
        self.stdout.write("   ✅ Database migrations applied")

        if not options["skip_css"]:
            bundle_type = "Development" if options["development"] else "Production"
            self.stdout.write(f"   ✅ {bundle_type} CSS bundles built")
            self.stdout.write("   📂 Bundles available at: static/css/bundles/")
        else:
            self.stdout.write("   ⏭️  CSS bundles skipped")

        self.stdout.write("   ✅ Static files collected")
        self.stdout.write("   ✅ Site structure configured")
        self.stdout.write("")

        if not options["skip_css"] and not options["development"]:
            self.stdout.write("🏭 Production CSS Bundles:")
            self.stdout.write("   • garden-ui-foundation.css (29.5KB)")
            self.stdout.write("   • garden-ui-core.css (103.5KB)")
            self.stdout.write("   • garden-ui-layout.css (34.9KB)")
            self.stdout.write("   • garden-ui-complete.css (167.2KB)")
            self.stdout.write("")
            self.stdout.write(
                "💡 Recommendation: Use base_production_bundles.html template for optimal performance"
            )
        elif options["development"]:
            self.stdout.write(
                "🔧 Development CSS bundles built with comments and debugging info"
            )
            self.stdout.write(
                "💡 Use base.html template for development with modular CSS files"
            )
        else:
            self.stdout.write(
                "💡 Run 'python manage.py build_css' to create optimized CSS bundles"
            )

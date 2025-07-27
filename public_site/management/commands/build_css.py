"""
Django management command for Garden UI CSS bundle building

Usage:
    python manage.py build_css
    python manage.py build_css --development
    python manage.py build_css --watch
"""

import subprocess
import sys
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Build Garden UI CSS bundles for production deployment"

    def add_arguments(self, parser):
        parser.add_argument(
            "--development",
            action="store_true",
            help="Build development bundle with comments and debugging info",
        )
        parser.add_argument(
            "--minify",
            action="store_true",
            help="Minify the output for production",
        )
        parser.add_argument(
            "--watch",
            action="store_true",
            help="Watch for file changes and rebuild automatically",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("🚀 Garden UI CSS Bundle Builder"))

        # Get project root
        project_root = Path(settings.BASE_DIR)
        script_path = project_root / "scripts" / "build_css.py"

        if not script_path.exists():
            self.stdout.write(
                self.style.ERROR(f"❌ Build script not found: {script_path}")
            )
            return

        # Build command arguments
        cmd = [sys.executable, str(script_path)]

        if options["development"]:
            cmd.append("--development")
            self.stdout.write("🔧 Building development bundles...")
        else:
            self.stdout.write("🏭 Building production bundles...")

        if options["minify"]:
            cmd.append("--minify")
            self.stdout.write("⚡ Minification enabled...")

        if options["watch"]:
            cmd.append("--watch")
            self.stdout.write("👀 File watching enabled...")

        try:
            # Run the build script
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)

            # Output results
            if result.stdout:
                self.stdout.write(result.stdout)

            if result.stderr:
                self.stdout.write(self.style.WARNING(result.stderr))

            if result.returncode == 0:
                self.stdout.write(
                    self.style.SUCCESS("✅ CSS bundles built successfully!")
                )

                # Show bundle location
                bundle_dir = project_root / "static" / "css" / "bundles"
                self.stdout.write(f"📁 Bundles available in: {bundle_dir}")

            else:
                self.stdout.write(
                    self.style.ERROR(f"❌ Build failed with code {result.returncode}")
                )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error running build script: {e}"))

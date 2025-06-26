from django.core.management.base import BaseCommand
from wagtail.models import Site

from public_site.models import HomePage, ProcessPage, ResearchPage


class Command(BaseCommand):
    help = "Set up missing research and process pages"

    def handle(self, *args, **options):
        try:
            # Get the default site and root page
            site = Site.objects.get(is_default_site=True)
            root_page = site.root_page

            # Get or create homepage
            homepage = HomePage.objects.first()
            if not homepage:
                self.stdout.write("Creating homepage...")
                homepage = HomePage(
                    title="Home",
                    slug="home",
                    hero_title="We're not like other firms. Good.",
                    hero_subtitle="Turning ethics into peace of mind through disciplined investment research",
                )
                root_page.add_child(instance=homepage)
                homepage.save_revision().publish()

                # Set as the site's root page
                site.root_page = homepage
                site.save()
                self.stdout.write(
                    self.style.SUCCESS("Homepage created and set as root page"),
                )
            else:
                self.stdout.write("Homepage already exists")

            # Create Research page
            research_page = ResearchPage.objects.filter(slug="research").first()
            if not research_page:
                self.stdout.write("Creating research page...")
                research_page = ResearchPage(
                    title="Research Methodology",
                    slug="research",
                    intro_text="Learn about our mission to democratize investment intelligence and compliance technology.",
                    methodology_content="Our research methodology combines proprietary analysis with transparent screening processes.",
                )
                homepage.add_child(instance=research_page)
                research_page.save_revision().publish()
                self.stdout.write(self.style.SUCCESS("Research page created"))
            else:
                self.stdout.write("Research page already exists")

            # Create Process page
            process_page = ProcessPage.objects.filter(slug="process").first()
            if not process_page:
                self.stdout.write("Creating process page...")
                process_page = ProcessPage(
                    title="Our Process",
                    slug="process",
                    intro_text="Learn about our mission to democratize investment intelligence and compliance technology.",
                    process_overview="Our investment process combines ethical screening with disciplined portfolio construction.",
                )
                homepage.add_child(instance=process_page)
                process_page.save_revision().publish()
                self.stdout.write(self.style.SUCCESS("Process page created"))
            else:
                self.stdout.write("Process page already exists")

            self.stdout.write(self.style.SUCCESS("Setup complete!"))
            self.stdout.write("You can now access:")
            self.stdout.write("- Research page: /research/")
            self.stdout.write("- Process page: /process/")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error setting up pages: {e!s}"))

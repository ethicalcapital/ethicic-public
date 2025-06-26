from django.core.management.base import BaseCommand

from public_site.models import AboutPage, HomePage, ProcessPage, ResearchPage


class Command(BaseCommand):
    help = "Setup proper ResearchPage and ProcessPage instances"

    def handle(self, *args, **options):
        try:
            # Get the homepage
            homepage = HomePage.objects.first()
            if not homepage:
                self.stdout.write(
                    self.style.ERROR("No homepage found. Please create one first."),
                )
                return

            # Remove old placeholder pages
            old_research = AboutPage.objects.filter(slug="research").first()
            if old_research:
                self.stdout.write("Removing old research placeholder...")
                old_research.delete()

            old_process = AboutPage.objects.filter(slug="process").first()
            if old_process:
                self.stdout.write("Removing old process placeholder...")
                old_process.delete()

            # Create proper ResearchPage
            if not ResearchPage.objects.filter(slug="research").exists():
                self.stdout.write("Creating ResearchPage...")
                research_page = ResearchPage(
                    title="Research Methodology",
                    slug="research",
                    intro_text="Learn about our mission to democratize investment intelligence and compliance technology.",
                    methodology_content="Our research methodology combines proprietary analysis with transparent screening processes.",
                    screening_title="Screening Process",
                    screening_content="We hand-screen thousands of companies, identifying ethical concerns that third-party ESG ratings often miss.",
                    analysis_title="Analysis Framework",
                    analysis_content="Our proprietary exclusions reflect deep, original analysis designed to enhance portfolio quality.",
                    transparency_title="Radical Transparency",
                    transparency_content='We "show the garage" - providing access to our exclusion lists, scoring methodologies, and research processes.',
                )
                homepage.add_child(instance=research_page)
                research_page.save_revision().publish()
                self.stdout.write(self.style.SUCCESS("ResearchPage created"))
            else:
                self.stdout.write("ResearchPage already exists")

            # Create proper ProcessPage
            if not ProcessPage.objects.filter(slug="process").exists():
                self.stdout.write("Creating ProcessPage...")
                process_page = ProcessPage(
                    title="Our Process",
                    slug="process",
                    intro_text="Learn about our mission to democratize investment intelligence and compliance technology.",
                    process_overview="Our investment process combines ethical screening with disciplined portfolio construction.",
                    step1_title="Ethical Screening",
                    step1_content="Comprehensive values alignment: BDS-compliant, fossil fuel free, tobacco free, weapons free.",
                    step2_title="Proprietary Research",
                    step2_content="Hand-screening of companies to identify concerns beyond standard ESG ratings.",
                    step3_title="Portfolio Construction",
                    step3_content="Disciplined diversification with concentration targets around 2% per holding.",
                    step4_title="Ongoing Monitoring",
                    step4_content="Continuous research updates and client partnership in identifying new concerns.",
                )
                homepage.add_child(instance=process_page)
                process_page.save_revision().publish()
                self.stdout.write(self.style.SUCCESS("ProcessPage created"))
            else:
                self.stdout.write("ProcessPage already exists")

            self.stdout.write(self.style.SUCCESS("Setup complete!"))
            self.stdout.write("Pages available at:")
            self.stdout.write("- Research: /research/")
            self.stdout.write("- Process: /process/")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e!s}"))

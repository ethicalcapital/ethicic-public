from django.core.management.base import BaseCommand

from public_site.models import AboutPage, ProcessPage, ResearchPage


class Command(BaseCommand):
    help = "Convert placeholder AboutPage instances to proper ResearchPage and ProcessPage types"

    def handle(self, *args, **options):
        try:
            # Find the research AboutPage and convert it
            research_about = AboutPage.objects.filter(slug="research").first()
            if research_about:
                self.stdout.write("Converting research AboutPage to ResearchPage...")

                # Create new ResearchPage
                research_page = ResearchPage(
                    title="Research Methodology",
                    slug="research",
                    depth=research_about.depth,
                    path=research_about.path,
                    intro_text="Learn about our mission to democratize investment intelligence and compliance technology.",
                    methodology_content="Our research methodology combines proprietary analysis with transparent screening processes.",
                    screening_title="Screening Process",
                    screening_content="We hand-screen thousands of companies, identifying ethical concerns that third-party ESG ratings often miss.",
                    analysis_title="Analysis Framework",
                    analysis_content="Our proprietary exclusions reflect deep, original analysis designed to enhance portfolio quality.",
                    transparency_title="Radical Transparency",
                    transparency_content='We "show the garage" - providing access to our exclusion lists, scoring methodologies, and research processes.',
                )

                # Copy essential page fields
                research_page.id = research_about.id
                research_page.content_type_id = ResearchPage._meta.get_field(
                    "content_type",
                ).get_default()

                # Delete the old page and save the new one
                research_about.delete()
                research_page.save()
                research_page.save_revision().publish()

                self.stdout.write(
                    self.style.SUCCESS("Research page converted to ResearchPage"),
                )
            else:
                self.stdout.write("No research AboutPage found")

            # Find the process AboutPage and convert it
            process_about = AboutPage.objects.filter(slug="process").first()
            if process_about:
                self.stdout.write("Converting process AboutPage to ProcessPage...")

                # Create new ProcessPage
                process_page = ProcessPage(
                    title="Our Process",
                    slug="process",
                    depth=process_about.depth,
                    path=process_about.path,
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

                # Copy essential page fields
                process_page.id = process_about.id
                process_page.content_type_id = ProcessPage._meta.get_field(
                    "content_type",
                ).get_default()

                # Delete the old page and save the new one
                process_about.delete()
                process_page.save()
                process_page.save_revision().publish()

                self.stdout.write(
                    self.style.SUCCESS("Process page converted to ProcessPage"),
                )
            else:
                self.stdout.write("No process AboutPage found")

            self.stdout.write(self.style.SUCCESS("Conversion complete!"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error converting pages: {e!s}"))

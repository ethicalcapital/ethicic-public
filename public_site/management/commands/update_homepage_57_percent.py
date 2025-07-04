from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Update homepage content from 68% to 57%"

    def handle(self, *args, **options):
        try:
            with connection.cursor() as cursor:
                # Update homepage sp500_excluded_pct
                cursor.execute(
                    "UPDATE public_site_homepage SET sp500_excluded_pct = %s WHERE sp500_excluded_pct = %s",
                    ["57%", "68%"]
                )
                homepage_rows = cursor.rowcount
                self.stdout.write(f"Updated {homepage_rows} homepage rows")

                # Update strategypage portfolio_content
                cursor.execute(
                    "UPDATE public_site_strategypage SET portfolio_content = REPLACE(portfolio_content, %s, %s) WHERE portfolio_content LIKE %s",
                    ["68%", "57%", "%68%"]
                )
                strategy_rows = cursor.rowcount
                self.stdout.write(f"Updated {strategy_rows} strategy page rows")

                # Update criteriapage criteria_description
                cursor.execute(
                    "UPDATE public_site_criteriapage SET criteria_description = REPLACE(criteria_description, %s, %s) WHERE criteria_description LIKE %s",
                    ["68%", "57%", "%68%"]
                )
                criteria_rows = cursor.rowcount
                self.stdout.write(f"Updated {criteria_rows} criteria page rows")

                # Verify no more 68% references exist
                cursor.execute("""
                    SELECT COUNT(*) FROM (
                        SELECT 1 FROM public_site_homepage WHERE
                            sp500_excluded_pct LIKE '%68%' OR
                            cta_description LIKE '%68%' OR
                            hero_description LIKE '%68%' OR
                            features_content LIKE '%68%'
                        UNION ALL
                        SELECT 1 FROM public_site_processpage WHERE process_overview LIKE '%68%'
                        UNION ALL
                        SELECT 1 FROM public_site_advisorpage WHERE hero_description LIKE '%68%'
                        UNION ALL
                        SELECT 1 FROM public_site_institutionalpage WHERE hero_description LIKE '%68%'
                        UNION ALL
                        SELECT 1 FROM public_site_criteriapage WHERE criteria_description LIKE '%68%'
                        UNION ALL
                        SELECT 1 FROM public_site_strategypage WHERE portfolio_content LIKE '%68%'
                    ) subquery
                """)
                remaining_count = cursor.fetchone()[0]

                if remaining_count == 0:
                    self.stdout.write(
                        self.style.SUCCESS("✅ Successfully updated all 68% references to 57%")
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f"⚠️  {remaining_count} 68% references still remain")
                    )

                # Clear Django cache
                from django.core.cache import cache
                cache.clear()
                self.stdout.write("✅ Cleared Django cache")

        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f"❌ Error updating content: {e}")
            )

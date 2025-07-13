import os

from django.core.management.base import BaseCommand
from django.utils import timezone

from public_site.models import StrategyPage


class Command(BaseCommand):
    help = "Import historical performance data from CSV files"

    def add_arguments(self, parser):
        parser.add_argument(
            "--csv-file", type=str, help="Path to the CSV file to import"
        )
        parser.add_argument(
            "--strategy-title",
            type=str,
            help='Title of the strategy page to update (e.g., "Growth Strategy")',
        )

    def handle(self, *args, **options):
        csv_file = options.get("csv_file")
        strategy_title = options.get("strategy_title")

        if not csv_file:
            self.stdout.write(self.style.ERROR("Please provide --csv-file argument"))
            return

        if not strategy_title:
            self.stdout.write(
                self.style.ERROR("Please provide --strategy-title argument")
            )
            return

        if not os.path.exists(csv_file):
            self.stdout.write(self.style.ERROR(f"CSV file not found: {csv_file}"))
            return

        try:
            strategy = StrategyPage.objects.get(title=strategy_title)
        except StrategyPage.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"Strategy page not found: {strategy_title}")
            )
            return

        # Parse CSV and import data
        monthly_returns = self.parse_csv(csv_file)

        if not monthly_returns:
            self.stdout.write(self.style.ERROR("No valid data found in CSV"))
            return

        # Update strategy with historical data
        strategy.monthly_returns = monthly_returns
        strategy.performance_last_updated = timezone.now()

        # Trigger performance calculations
        strategy._update_calculated_performance()
        strategy.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully imported performance data for {strategy_title}\n"
                f"Updated {len(monthly_returns)} years of data"
            )
        )

    def parse_csv(self, csv_file):
        """Parse the performance CSV file and return structured data."""
        monthly_returns = {}

        with open(csv_file) as f:
            # Skip the header rows and find the data
            lines = f.readlines()

        current_year = None
        strategy_row = None
        benchmark_row = None

        for _line_num, line in enumerate(lines):
            if not line.strip():
                continue

            parts = [p.strip() for p in line.split(",")]

            # Look for year headers (e.g., ",2025,Jan,Feb,Mar...")
            if len(parts) > 1 and parts[1].isdigit() and len(parts[1]) == 4:
                current_year = parts[1]
                parts[2:14]  # Get the month names
                continue

            # Look for Strategy TWR rows
            if len(parts) > 1 and "Strategy TWR" in parts[1]:
                strategy_row = parts[2:14]  # Get the monthly values

            # Look for benchmark rows (MSCI ACWI TR or Benchmark TR)
            if len(parts) > 1 and (
                "MSCI ACWI TR" in parts[1] or "Benchmark TR" in parts[1]
            ):
                benchmark_row = parts[2:14]  # Get the monthly values

                # When we have both strategy and benchmark for a year, process it
                if current_year and strategy_row and benchmark_row:
                    monthly_returns[current_year] = {}

                    months = [
                        "Jan",
                        "Feb",
                        "Mar",
                        "Apr",
                        "May",
                        "Jun",
                        "Jul",
                        "Aug",
                        "Sep",
                        "Oct",
                        "Nov",
                        "Dec",
                    ]

                    for i, month in enumerate(months):
                        if i < len(strategy_row) and i < len(benchmark_row):
                            strategy_val = strategy_row[i].strip()
                            benchmark_val = benchmark_row[i].strip()

                            # Only add if both values are valid percentages
                            if (
                                strategy_val
                                and benchmark_val
                                and "%" in strategy_val
                                and "%" in benchmark_val
                                and strategy_val != ""
                                and benchmark_val != ""
                            ):
                                monthly_returns[current_year][month] = {
                                    "strategy": strategy_val,
                                    "benchmark": benchmark_val,
                                }

                    # Reset for next year
                    strategy_row = None
                    benchmark_row = None

        return monthly_returns


if __name__ == "__main__":
    # Example usage
    print("Example usage:")
    print(
        "python manage.py import_performance_csv --csv-file growth_performance.csv --strategy-title 'Growth Strategy'"
    )

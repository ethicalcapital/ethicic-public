from django.core.management.base import BaseCommand
from public_site.models import StrategyPage


class Command(BaseCommand):
    help = "Display current performance data for all strategy pages"

    def add_arguments(self, parser):
        parser.add_argument(
            '--strategy',
            type=str,
            help='Show performance for specific strategy (optional)'
        )

    def handle(self, *args, **options):
        strategy_name = options.get('strategy')
        
        if strategy_name:
            try:
                strategies = [StrategyPage.objects.get(title=strategy_name)]
            except StrategyPage.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Strategy not found: {strategy_name}')
                )
                return
        else:
            strategies = StrategyPage.objects.all()

        for strategy in strategies:
            self.stdout.write(
                self.style.SUCCESS(f'\n📊 {strategy.title} Strategy Performance')
            )
            self.stdout.write('=' * 50)
            
            if strategy.inception_date:
                self.stdout.write(f'Inception Date: {strategy.inception_date}')
            
            if strategy.performance_last_updated:
                self.stdout.write(f'Last Updated: {strategy.performance_last_updated.strftime("%Y-%m-%d %H:%M")}')
            
            self.stdout.write('\nPerformance Metrics:')
            self.stdout.write(f'  YTD Return:          {strategy.ytd_return or "N/A"} (vs {strategy.ytd_benchmark or "N/A"} benchmark)')
            self.stdout.write(f'  1-Year Return:       {strategy.one_year_return or "N/A"} (vs {strategy.one_year_benchmark or "N/A"} benchmark)')
            self.stdout.write(f'  3-Year Return:       {strategy.three_year_return or "N/A"} (vs {strategy.three_year_benchmark or "N/A"} benchmark)')
            self.stdout.write(f'  Since Inception:     {strategy.since_inception_return or "N/A"} (vs {strategy.since_inception_benchmark or "N/A"} benchmark)')
            
            # Show latest few months of data
            if strategy.monthly_returns:
                self.stdout.write('\nRecent Monthly Returns:')
                years = sorted(strategy.monthly_returns.keys(), reverse=True)
                months_shown = 0
                
                for year in years:
                    if months_shown >= 6:  # Show last 6 months
                        break
                        
                    year_data = strategy.monthly_returns[year]
                    month_order = ['Dec', 'Nov', 'Oct', 'Sep', 'Aug', 'Jul', 'Jun', 'May', 'Apr', 'Mar', 'Feb', 'Jan']
                    
                    for month in month_order:
                        if months_shown >= 6:
                            break
                        if month in year_data:
                            data = year_data[month]
                            self.stdout.write(f'  {month} {year}: {data.get("strategy", "N/A")} (vs {data.get("benchmark", "N/A")})')
                            months_shown += 1

        if not strategy_name:
            self.stdout.write(
                self.style.WARNING(
                    '\n💡 To update performance, go to /cms/ and edit a strategy page, '
                    'then enter new monthly data in the "Performance Update" section.'
                )
            )
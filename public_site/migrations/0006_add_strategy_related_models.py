# Generated manually to add missing Strategy-related models

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('public_site', '0005_alter_strategypage_performance_disclaimer'),
    ]

    operations = [
        # Create StrategyRiskMetric
        migrations.CreateModel(
            name='StrategyRiskMetric',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('standard_deviation', models.CharField(blank=True, help_text='e.g., 16.2%', max_length=20)),
                ('sharpe_ratio', models.CharField(blank=True, help_text='e.g., 0.78', max_length=20)),
                ('max_drawdown', models.CharField(blank=True, help_text='e.g., -22.1%', max_length=20)),
                ('beta', models.CharField(blank=True, help_text='e.g., 0.94', max_length=20)),
                ('page', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='risk_metrics', to='public_site.strategypage')),
            ],
        ),
        
        # Create StrategyGeographicAllocation
        migrations.CreateModel(
            name='StrategyGeographicAllocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('region', models.CharField(max_length=100)),
                ('allocation_percent', models.CharField(max_length=20, help_text='e.g., 73.1%')),
                ('benchmark_percent', models.CharField(blank=True, max_length=20, help_text='e.g., 62.3%')),
                ('difference_percent', models.CharField(blank=True, max_length=20, help_text='e.g., +10.8%')),
                ('page', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='geographic_allocations', to='public_site.strategypage')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        
        # Create StrategySectorPosition
        migrations.CreateModel(
            name='StrategySectorPosition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('sector_name', models.CharField(max_length=100)),
                ('position_type', models.CharField(choices=[('overweight', 'Overweight'), ('underweight', 'Underweight'), ('exclusion', 'Exclusion')], max_length=20)),
                ('note', models.CharField(blank=True, max_length=300)),
                ('page', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='sector_positions', to='public_site.strategypage')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        
        # Create StrategyHolding
        migrations.CreateModel(
            name='StrategyHolding',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('company_name', models.CharField(max_length=200)),
                ('ticker_symbol', models.CharField(max_length=10)),
                ('weight_percent', models.CharField(max_length=20, help_text='e.g., 3.5%')),
                ('vertical', models.CharField(max_length=100)),
                ('investment_thesis', models.TextField()),
                ('key_metrics', models.TextField()),
                ('page', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='holdings', to='public_site.strategypage')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        
        # Create StrategyVerticalAllocation
        migrations.CreateModel(
            name='StrategyVerticalAllocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('vertical_name', models.CharField(max_length=100)),
                ('weight_percent', models.CharField(max_length=20)),
                ('dividend_yield', models.CharField(blank=True, max_length=20)),
                ('pe_ratio', models.CharField(blank=True, max_length=20)),
                ('revenue_cagr', models.CharField(blank=True, max_length=20)),
                ('fcf_market_cap', models.CharField(blank=True, max_length=20)),
                ('is_total_row', models.BooleanField(default=False)),
                ('is_benchmark_row', models.BooleanField(default=False)),
                ('page', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='vertical_allocations', to='public_site.strategypage')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        
        # Create StrategyDocument
        migrations.CreateModel(
            name='StrategyDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('title', models.CharField(max_length=200)),
                ('description', models.CharField(max_length=300)),
                ('category', models.CharField(choices=[('factsheet', 'Fact Sheets'), ('report', 'Reports'), ('prospectus', 'Prospectus & Legal'), ('other', 'Other Documents')], default='factsheet', max_length=20)),
                ('document_url', models.URLField(blank=True, help_text='External URL for the document')),
                ('icon', models.CharField(default='📄', max_length=10, help_text='Emoji or icon for the document')),
                ('page', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='public_site.strategypage')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
    ]
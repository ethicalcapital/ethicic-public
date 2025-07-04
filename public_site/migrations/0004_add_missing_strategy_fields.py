# Generated manually to add missing StrategyPage fields

from django.db import migrations, models
import wagtail.fields


class Migration(migrations.Migration):
    dependencies = [
        ("public_site", "0003_add_editable_fields_to_pages"),
    ]

    operations = [
        migrations.AddField(
            model_name="strategypage",
            name="cash_allocation",
            field=models.CharField(blank=True, default="0.93%", max_length=20),
        ),
        migrations.AddField(
            model_name="strategypage",
            name="benchmark_name",
            field=models.CharField(
                blank=True,
                default="ACWI",
                help_text="e.g., ACWI, AGG/PFF, S&P 500",
                max_length=50,
            ),
        ),
        migrations.AddField(
            model_name="strategypage",
            name="ytd_benchmark",
            field=models.CharField(blank=True, default="5.1%", max_length=20),
        ),
        migrations.AddField(
            model_name="strategypage",
            name="ytd_difference",
            field=models.CharField(blank=True, default="+3.1%", max_length=20),
        ),
        migrations.AddField(
            model_name="strategypage",
            name="one_year_benchmark",
            field=models.CharField(blank=True, default="12.3%", max_length=20),
        ),
        migrations.AddField(
            model_name="strategypage",
            name="one_year_difference",
            field=models.CharField(blank=True, default="+3.4%", max_length=20),
        ),
        migrations.AddField(
            model_name="strategypage",
            name="three_year_benchmark",
            field=models.CharField(blank=True, default="7.2%", max_length=20),
        ),
        migrations.AddField(
            model_name="strategypage",
            name="three_year_difference",
            field=models.CharField(blank=True, default="+2.6%", max_length=20),
        ),
        migrations.AddField(
            model_name="strategypage",
            name="since_inception_benchmark",
            field=models.CharField(blank=True, default="9.5%", max_length=20),
        ),
        migrations.AddField(
            model_name="strategypage",
            name="since_inception_difference",
            field=models.CharField(blank=True, default="+2.6%", max_length=20),
        ),
        migrations.AddField(
            model_name="strategypage",
            name="overweights_note",
            field=models.CharField(
                blank=True, default="Higher conviction in these sectors", max_length=300
            ),
        ),
        migrations.AddField(
            model_name="strategypage",
            name="exclusions_note",
            field=models.CharField(
                blank=True, default="22% of benchmark index excluded", max_length=300
            ),
        ),
        migrations.AddField(
            model_name="strategypage",
            name="healthcare_exclusion_note",
            field=models.TextField(
                blank=True,
                default="* Healthcare exclusions are selective, focused on companies that directly support abortion procedures or controversial research practices",
            ),
        ),
        migrations.AddField(
            model_name="strategypage",
            name="performance_disclaimer",
            field=wagtail.fields.RichTextField(
                blank=True, help_text="Performance disclaimer text"
            ),
        ),
    ]

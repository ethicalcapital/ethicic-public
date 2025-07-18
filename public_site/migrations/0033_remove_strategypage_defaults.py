# Generated by Django 4.2.11 on 2025-07-11 12:00

from django.db import migrations, models
import wagtail.fields


def preserve_strategy_defaults(apps, schema_editor):
    """
    Preserve existing hardcoded defaults by setting them on existing records
    that have empty/null values.
    """
    StrategyPage = apps.get_model("public_site", "StrategyPage")

    # Dictionary of fields and their default values
    defaults = {
        "risk_level": "Full market exposure",
        "ethical_implementation": "100% Full Criteria",
        "holdings_count": "15-25",
        "best_for": "Long-term growth",
        "cash_allocation": "0.93%",
        "benchmark_name": "ACWI",
        "ytd_return": "8.2%",
        "ytd_benchmark": "5.1%",
        "ytd_difference": "+3.1%",
        "one_year_return": "15.7%",
        "one_year_benchmark": "12.3%",
        "one_year_difference": "+3.4%",
        "three_year_return": "9.8%",
        "three_year_benchmark": "7.2%",
        "three_year_difference": "+2.6%",
        "since_inception_return": "12.1%",
        "since_inception_benchmark": "9.5%",
        "since_inception_difference": "+2.6%",
        "overweights_note": "Higher conviction in these sectors",
        "exclusions_note": "22% of benchmark index excluded",
        "healthcare_exclusion_note": "* Healthcare exclusions are selective, focused on companies that directly support abortion procedures or controversial research practices",
        "commentary_title": "Strategy Commentary",
        "process_title": "Our Process",
        "documents_title": "Strategy Documents",
        "performance_disclaimer": "<p>Past performance is not indicative of future results. Investment returns and principal value will fluctuate.</p>",
    }

    # Apply defaults to existing records where fields are empty
    for strategy in StrategyPage.objects.all():
        updated = False
        for field_name, default_value in defaults.items():
            current_value = getattr(strategy, field_name, None)
            if not current_value or current_value.strip() == "":
                setattr(strategy, field_name, default_value)
                updated = True

        if updated:
            strategy.save()
            print(f"Updated StrategyPage: {strategy.title}")


def reverse_preserve_strategy_defaults(apps, schema_editor):
    """
    Reverse migration - clear the fields that were set by defaults
    """
    # Note: This is a one-way operation for data preservation
    # We don't actually clear the data in reverse
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("public_site", "0032_remove_processpage_defaults"),
    ]

    operations = [
        # First, preserve existing content
        migrations.RunPython(
            preserve_strategy_defaults,
            reverse_preserve_strategy_defaults,
        ),
        # Then remove the default parameters from fields
        migrations.AlterField(
            model_name="strategypage",
            name="risk_level",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="strategypage",
            name="ethical_implementation",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="strategypage",
            name="holdings_count",
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name="strategypage",
            name="best_for",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="strategypage",
            name="cash_allocation",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AlterField(
            model_name="strategypage",
            name="benchmark_name",
            field=models.CharField(
                blank=True, help_text="e.g., ACWI, AGG/PFF, S&P 500", max_length=50
            ),
        ),
        migrations.AlterField(
            model_name="strategypage",
            name="ytd_return",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AlterField(
            model_name="strategypage",
            name="ytd_benchmark",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AlterField(
            model_name="strategypage",
            name="ytd_difference",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AlterField(
            model_name="strategypage",
            name="one_year_return",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AlterField(
            model_name="strategypage",
            name="one_year_benchmark",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AlterField(
            model_name="strategypage",
            name="one_year_difference",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AlterField(
            model_name="strategypage",
            name="three_year_return",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AlterField(
            model_name="strategypage",
            name="three_year_benchmark",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AlterField(
            model_name="strategypage",
            name="three_year_difference",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AlterField(
            model_name="strategypage",
            name="since_inception_return",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AlterField(
            model_name="strategypage",
            name="since_inception_benchmark",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AlterField(
            model_name="strategypage",
            name="since_inception_difference",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AlterField(
            model_name="strategypage",
            name="overweights_note",
            field=models.CharField(blank=True, max_length=300),
        ),
        migrations.AlterField(
            model_name="strategypage",
            name="exclusions_note",
            field=models.CharField(blank=True, max_length=300),
        ),
        migrations.AlterField(
            model_name="strategypage",
            name="healthcare_exclusion_note",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="strategypage",
            name="commentary_title",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name="strategypage",
            name="process_title",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name="strategypage",
            name="documents_title",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name="strategypage",
            name="performance_disclaimer",
            field=wagtail.fields.RichTextField(blank=True),
        ),
    ]

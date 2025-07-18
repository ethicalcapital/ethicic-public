# Generated by Django 4.2.14 on 2025-07-11 14:30

from django.db import migrations, models
import wagtail.fields


class Migration(migrations.Migration):
    dependencies = [
        ("public_site", "0034_remove_priddqpage_defaults"),
    ]

    operations = [
        # ContactFormPage field modifications
        migrations.AlterField(
            model_name="contactformpage",
            name="intro_text",
            field=wagtail.fields.RichTextField(blank=True),
        ),
        migrations.AlterField(
            model_name="contactformpage",
            name="form_description",
            field=wagtail.fields.RichTextField(blank=True),
        ),
        migrations.AlterField(
            model_name="contactformpage",
            name="thank_you_title",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name="contactformpage",
            name="thank_you_message",
            field=wagtail.fields.RichTextField(blank=True),
        ),
        migrations.AlterField(
            model_name="contactformpage",
            name="enable_form",
            field=models.BooleanField(blank=True),
        ),
        migrations.AlterField(
            model_name="contactformpage",
            name="require_phone",
            field=models.BooleanField(
                blank=True, help_text="Require phone number field"
            ),
        ),
        migrations.AlterField(
            model_name="contactformpage",
            name="contact_section_title",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name="contactformpage",
            name="contact_email",
            field=models.EmailField(
                blank=True, help_text="Primary contact email address", max_length=254
            ),
        ),
        migrations.AlterField(
            model_name="contactformpage",
            name="contact_phone",
            field=models.CharField(
                blank=True, help_text="Primary contact phone number", max_length=20
            ),
        ),
        migrations.AlterField(
            model_name="contactformpage",
            name="contact_address",
            field=models.CharField(
                blank=True, help_text="Business address", max_length=200
            ),
        ),
        migrations.AlterField(
            model_name="contactformpage",
            name="business_hours",
            field=models.CharField(
                blank=True, help_text="Business hours", max_length=200
            ),
        ),
        migrations.AlterField(
            model_name="contactformpage",
            name="show_consultation_sidebar",
            field=models.BooleanField(
                blank=True, help_text="Show consultation scheduling sidebar"
            ),
        ),
        migrations.AlterField(
            model_name="contactformpage",
            name="consultation_sidebar_title",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name="contactformpage",
            name="consultation_sidebar_description",
            field=wagtail.fields.RichTextField(blank=True),
        ),
        migrations.AlterField(
            model_name="contactformpage",
            name="consultation_sidebar_button_text",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="contactformpage",
            name="consultation_sidebar_button_url",
            field=models.CharField(blank=True, max_length=200),
        ),
        # SolutionsPage field modifications
        migrations.AlterField(
            model_name="solutionspage",
            name="hero_title",
            field=models.CharField(
                blank=True, help_text="Main headline", max_length=200
            ),
        ),
        migrations.AlterField(
            model_name="solutionspage",
            name="hero_subtitle",
            field=models.TextField(
                blank=True,
                help_text="Subtitle text below the main headline",
                max_length=500,
            ),
        ),
        migrations.AlterField(
            model_name="solutionspage",
            name="hero_description",
            field=wagtail.fields.RichTextField(
                blank=True, help_text="Hero section description"
            ),
        ),
        migrations.AlterField(
            model_name="solutionspage",
            name="strategies_section_title",
            field=models.CharField(
                blank=True, help_text="Title for strategies section", max_length=200
            ),
        ),
        migrations.AlterField(
            model_name="solutionspage",
            name="strategies_intro",
            field=models.TextField(
                blank=True, help_text="Introduction text for strategies section"
            ),
        ),
        migrations.AlterField(
            model_name="solutionspage",
            name="individuals_title",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name="solutionspage",
            name="individuals_content",
            field=wagtail.fields.RichTextField(blank=True),
        ),
        migrations.AlterField(
            model_name="solutionspage",
            name="institutions_title",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name="solutionspage",
            name="institutions_content",
            field=wagtail.fields.RichTextField(blank=True),
        ),
        migrations.AlterField(
            model_name="solutionspage",
            name="advisors_title",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name="solutionspage",
            name="advisors_content",
            field=wagtail.fields.RichTextField(blank=True),
        ),
        migrations.AlterField(
            model_name="solutionspage",
            name="cta_title",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name="solutionspage",
            name="cta_description",
            field=wagtail.fields.RichTextField(blank=True),
        ),
    ]

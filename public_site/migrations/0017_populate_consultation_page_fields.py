# Generated by Django 5.1.5 on 2025-07-07 00:27

from django.db import migrations
import json


def populate_consultation_page_fields(apps, schema_editor):
    """Populate ConsultationPage with hardcoded content from template."""
    ConsultationPage = apps.get_model("public_site", "ConsultationPage")

    # Get all ConsultationPage instances
    for page in ConsultationPage.objects.all():
        # Consultation types
        if not page.consultation_types:
            page.consultation_types = json.dumps(
                [
                    {
                        "type": "consultation_type",
                        "value": {
                            "icon": "🏠",
                            "title": "Retail Investors",
                            "description": "Individual investors looking to align their personal portfolios with their values",
                            "button_text": "Schedule Discovery Call",
                            "button_url": "https://tidycal.com/ecic/discovery",
                        },
                    },
                    {
                        "type": "consultation_type",
                        "value": {
                            "icon": "💼",
                            "title": "RIA & Advisers",
                            "description": "Financial advisers interested in our investment strategies for their clients",
                            "button_text": "Schedule Adviser Meeting",
                            "button_url": "https://tidycal.com/ecic/adviser",
                        },
                    },
                    {
                        "type": "consultation_type",
                        "value": {
                            "icon": "🏢",
                            "title": "Institutional",
                            "description": "Institutional investors, foundations, and large-scale investment opportunities",
                            "button_text": "Schedule Institutional Call",
                            "button_url": "https://tidycal.com/ecic/institutional",
                        },
                    },
                ]
            )

        # Expectations
        if not page.expectations:
            page.expectations = json.dumps(
                [
                    {
                        "type": "expectation",
                        "value": {
                            "title": "Initial Conversation",
                            "description": "We'll discuss your values, investment goals, and current portfolio situation.",
                        },
                    },
                    {
                        "type": "expectation",
                        "value": {
                            "title": "Ethical Alignment Review",
                            "description": "We'll review how our screening criteria align with your personal values.",
                        },
                    },
                    {
                        "type": "expectation",
                        "value": {
                            "title": "Strategy Discussion",
                            "description": "We'll explore which of our strategies might be the best fit for your needs.",
                        },
                    },
                    {
                        "type": "expectation",
                        "value": {
                            "title": "Next Steps",
                            "description": "If we're a good fit, we'll outline the onboarding process and timeline.",
                        },
                    },
                ]
            )

        page.save()


def reverse_population(apps, schema_editor):
    """Reverse migration - no need to clear fields."""
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("public_site", "0016_add_consultation_page_fields"),
    ]

    operations = [
        migrations.RunPython(populate_consultation_page_fields, reverse_population),
    ]

# Generated by Django 5.1.5 on 2025-07-07 00:32

from django.db import migrations
import json


def populate_strategy_list_fields(apps, schema_editor):
    """Populate StrategyListPage with hardcoded content from template."""
    StrategyListPage = apps.get_model("public_site", "StrategyListPage")

    # Get all StrategyListPage instances
    for page in StrategyListPage.objects.all():
        # Resources
        if not page.resources:
            page.resources = json.dumps(
                [
                    {
                        "type": "resource_category",
                        "value": {
                            "title": "Investment Process",
                            "description": "Systematic four-step approach combining quantitative analysis with ethical screening",
                            "links": [
                                {"text": "Our Investment Process", "url": "/process/"},
                                {
                                    "text": "Ethical Screening Criteria",
                                    "url": "https://github.com/ethicalcapital/sage/blob/main/screening_policy.md",
                                },
                            ],
                        },
                    },
                    {
                        "type": "resource_category",
                        "value": {
                            "title": "Due Diligence",
                            "description": "Comprehensive documentation for institutional due diligence processes",
                            "links": [
                                {
                                    "text": "PRI Due Diligence Questionnaire",
                                    "url": "/pri-ddq/",
                                },
                                {"text": "Form ADV", "url": "/disclosures/form-adv/"},
                            ],
                        },
                    },
                    {
                        "type": "resource_category",
                        "value": {
                            "title": "Performance & Reporting",
                            "description": "Transparent performance tracking and comprehensive client reporting",
                            "links": [
                                {
                                    "text": "Historical Performance",
                                    "url": "/performance/",
                                },
                                {"text": "All Disclosures", "url": "/disclosures/"},
                            ],
                        },
                    },
                ]
            )

        # CTA buttons
        if not page.cta_buttons:
            page.cta_buttons = json.dumps(
                [
                    {
                        "type": "cta_button",
                        "value": {
                            "text": "SCHEDULE CONSULTATION",
                            "url": "/consultation/",
                            "style": "primary",
                        },
                    },
                    {
                        "type": "cta_button",
                        "value": {
                            "text": "START ONBOARDING",
                            "url": "/onboarding/",
                            "style": "secondary",
                        },
                    },
                    {
                        "type": "cta_button",
                        "value": {
                            "text": "LEARN OUR PROCESS",
                            "url": "/process/",
                            "style": "secondary",
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
        ("public_site", "0019_add_strategy_list_resources_cta"),
    ]

    operations = [
        migrations.RunPython(populate_strategy_list_fields, reverse_population),
    ]

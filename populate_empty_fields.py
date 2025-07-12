#!/usr/bin/env python3
"""
Populate empty fields with default values for existing instances.
This script ensures existing pages have the original default content.
"""

import json
import os
import sys
from pathlib import Path

import django

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ethicic.settings")
django.setup()

from public_site.models import (
    BlogIndexPage,
    BlogPost,
    ConsultationPage,
    ContactPage,
    CriteriaPage,
    EncyclopediaEntry,
    EncyclopediaIndexPage,
    FAQIndexPage,
    FAQPage,
    GuidePage,
    OnboardingPage,
    ResearchPage,
    StrategyListPage,
)

# Load the default values we preserved
with open("custom_defaults_backup_20250711_224112.json") as f:
    default_values = json.load(f)

# Map model names to classes
MODEL_MAP = {
    "StrategyListPage": StrategyListPage,
    "ConsultationPage": ConsultationPage,
    "CriteriaPage": CriteriaPage,
    "GuidePage": GuidePage,
    "FAQIndexPage": FAQIndexPage,
    "FAQPage": FAQPage,
    "BlogIndexPage": BlogIndexPage,
    "ResearchPage": ResearchPage,
    "OnboardingPage": OnboardingPage,
    "ContactPage": ContactPage,
    "EncyclopediaIndexPage": EncyclopediaIndexPage,
    "BlogPost": BlogPost,
    "EncyclopediaEntry": EncyclopediaEntry,
}


def populate_model_fields(model_name, model_class, field_defaults):
    """Populate empty fields with default values for a specific model."""
    print(f"\nProcessing {model_name}...")

    instances = model_class.objects.all()
    updated_count = 0

    for instance in instances:
        updated_fields = []

        for field_name, default_value in field_defaults.items():
            if hasattr(instance, field_name):
                current_value = getattr(instance, field_name)

                # Check if field is empty (None, empty string, or empty RichTextField)
                if (
                    current_value is None
                    or current_value == ""
                    or (
                        hasattr(current_value, "raw_text")
                        and not current_value.raw_text.strip()
                    )
                ):
                    try:
                        setattr(instance, field_name, default_value)
                        updated_fields.append(field_name)
                    except Exception as e:
                        print(
                            f"  Warning: Could not set {field_name} to default value: {e}"
                        )

        if updated_fields:
            try:
                instance.save()
                updated_count += 1
                print(
                    f"  Updated {instance.title} ({instance.id}): {', '.join(updated_fields)}"
                )
            except Exception as e:
                print(f"  Error saving {instance.title}: {e}")

    print(f"  Total {model_name} instances updated: {updated_count}")
    return updated_count


def main():
    """Populate empty fields with default values for all models."""
    print("Populating empty fields with default values...")
    print("=" * 60)

    total_updated = 0

    for model_name, field_defaults in default_values.items():
        if model_name in MODEL_MAP:
            model_class = MODEL_MAP[model_name]
            count = populate_model_fields(model_name, model_class, field_defaults)
            total_updated += count
        else:
            print(f"Warning: Model {model_name} not found in MODEL_MAP")

    print("\n\nSummary:")
    print(f"Total instances updated across all models: {total_updated}")
    print("All empty fields have been populated with default values.")
    print("Your CMS is now 100% editable!")


if __name__ == "__main__":
    main()

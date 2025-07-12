#!/usr/bin/env python3
"""
Preserve current content from all 13 models before removing default values.
This script creates a complete backup of all existing content.
"""

import json
import os
import sys
from datetime import datetime
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

# Target models
TARGET_MODELS = {
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


def serialize_field_value(value):
    """Serialize field values for JSON storage."""
    if hasattr(value, "raw_text"):  # RichTextField
        return value.raw_text
    elif hasattr(value, "stream_data"):  # StreamField
        return value.stream_data
    elif hasattr(value, "file"):  # FileField/ImageField
        return value.file.name if value.file else None
    else:
        return str(value) if value is not None else None


def extract_model_content(model_class):
    """Extract current content from all instances of a model."""
    instances = []

    for instance in model_class.objects.all():
        instance_data = {
            "id": instance.id,
            "title": instance.title,
            "slug": instance.slug,
            "fields": {},
        }

        # Get all fields with content
        for field in instance._meta.get_fields():
            if hasattr(instance, field.name):
                try:
                    value = getattr(instance, field.name)
                    if value is not None:
                        instance_data["fields"][field.name] = serialize_field_value(
                            value
                        )
                except Exception as e:
                    print(f"Warning: Could not serialize field {field.name}: {e}")

        instances.append(instance_data)

    return instances


def main():
    """Extract and save content from all target models."""
    print("Preserving content from all target models...")
    print("=" * 60)

    all_content = {}

    for model_name, model_class in TARGET_MODELS.items():
        print(f"\nProcessing {model_name}...")

        try:
            instances = extract_model_content(model_class)
            all_content[model_name] = instances

            print(f"  Found {len(instances)} instances")

            # Show sample of content preserved
            if instances:
                sample = instances[0]
                print(
                    f"  Sample fields: {', '.join(list(sample['fields'].keys())[:5])}"
                )

        except Exception as e:
            print(f"  Error processing {model_name}: {e}")
            all_content[model_name] = []

    # Save complete backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"content_backup_before_migration_{timestamp}.json"

    with open(filename, "w") as f:
        json.dump(all_content, f, indent=2, default=str)

    print(f"\n\nContent backup saved to: {filename}")

    # Summary
    total_instances = sum(len(instances) for instances in all_content.values())
    print(f"Total instances preserved: {total_instances}")

    # Show summary by model
    print("\nSummary by model:")
    for model_name, instances in all_content.items():
        print(f"  {model_name}: {len(instances)} instances")

    return all_content


if __name__ == "__main__":
    main()

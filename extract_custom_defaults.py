#!/usr/bin/env python3
"""
Extract and save custom default values from the 13 models that need to be updated.
This script filters out system defaults and focuses on content defaults.
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

# Fields that are system defaults we should ignore
SYSTEM_FIELDS = {
    "translation_key",
    "locale",
    "latest_revision",
    "live",
    "has_unpublished_changes",
    "first_published_at",
    "last_published_at",
    "live_revision",
    "go_live_at",
    "expire_at",
    "expired",
    "locked",
    "locked_at",
    "locked_by",
    "title",
    "draft_title",
    "slug",
    "content_type",
    "url_path",
    "owner",
    "seo_title",
    "show_in_menus",
    "search_description",
    "latest_revision_created_at",
    "alias_of",
    "page_ptr",
    "_revisions",
    "_workflow_states",
    "_specific_workflow_states",
    "index_entries",
    "id",
    "path",
    "depth",
    "numchild",
}

# Target models and their expected field counts
TARGET_MODELS = {
    "StrategyListPage": (StrategyListPage, 10),
    "ConsultationPage": (ConsultationPage, 9),
    "CriteriaPage": (CriteriaPage, 8),
    "GuidePage": (GuidePage, 7),
    "FAQIndexPage": (FAQIndexPage, 6),
    "FAQPage": (FAQPage, 5),
    "BlogIndexPage": (BlogIndexPage, 4),
    "ResearchPage": (ResearchPage, 4),
    "OnboardingPage": (OnboardingPage, 4),
    "ContactPage": (ContactPage, 2),
    "EncyclopediaIndexPage": (EncyclopediaIndexPage, 2),
    "BlogPost": (BlogPost, 1),
    "EncyclopediaEntry": (EncyclopediaEntry, 1),
}


def extract_custom_defaults(model_class):
    """Extract custom default values, excluding system defaults."""
    custom_defaults = {}

    for field in model_class._meta.get_fields():
        # Skip system fields
        if field.name in SYSTEM_FIELDS:
            continue

        # Check if field has a non-None default that's not a system value
        if hasattr(field, "default"):
            default_value = field.default

            # Skip NOT_PROVIDED and None values
            if (
                default_value is None
                or str(default_value) == "django.db.models.fields.NOT_PROVIDED"
            ):
                continue

            # Skip function defaults (like uuid4)
            if callable(default_value):
                continue

            # Skip certain boolean defaults that are system-related
            if isinstance(default_value, bool) and field.name in [
                "featured",
                "show_contact_form",
                "enable_form",
            ]:
                pass  # These are meaningful content defaults
            elif isinstance(default_value, bool):
                continue  # Skip other boolean system defaults

            # Skip numeric defaults that look like system defaults
            if isinstance(default_value, (int, float)) and field.name in [
                "reading_time"
            ]:
                pass  # This is a meaningful content default
            elif isinstance(default_value, (int, float)):
                continue

            # This is a custom content default
            custom_defaults[field.name] = default_value

    return custom_defaults


def main():
    """Extract and save custom defaults for all target models."""
    print("Extracting custom default values from target models...")
    print("=" * 60)

    all_defaults = {}

    for model_name, (model_class, expected_count) in TARGET_MODELS.items():
        print(f"\n{model_name}:")
        print("-" * 40)

        custom_defaults = extract_custom_defaults(model_class)
        all_defaults[model_name] = custom_defaults

        if custom_defaults:
            print(f"Found {len(custom_defaults)} custom default fields:")
            for field_name, default_value in custom_defaults.items():
                print(f"  {field_name}: {repr(default_value)}")
        else:
            print("  No custom default fields found")

        # Check if count matches expectation
        if len(custom_defaults) != expected_count:
            print(
                f"  WARNING: Expected {expected_count} fields, found {len(custom_defaults)}"
            )

    # Save to JSON file for preservation
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"custom_defaults_backup_{timestamp}.json"

    with open(filename, "w") as f:
        json.dump(all_defaults, f, indent=2, default=str)

    print(f"\n\nCustom defaults saved to: {filename}")
    print(f"Total models processed: {len(all_defaults)}")

    # Summary
    total_fields = sum(len(defaults) for defaults in all_defaults.values())
    print(f"Total custom default fields found: {total_fields}")

    return all_defaults


if __name__ == "__main__":
    main()

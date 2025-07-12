#!/usr/bin/env python3
"""
Script to extract all fields with default values from the 13 remaining models.
This will help us understand what needs to be preserved before removing defaults.
"""

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

# Target models to analyze
TARGET_MODELS = [
    StrategyListPage,
    ConsultationPage,
    CriteriaPage,
    GuidePage,
    FAQIndexPage,
    FAQPage,
    BlogIndexPage,
    ResearchPage,
    OnboardingPage,
    ContactPage,
    EncyclopediaIndexPage,
    BlogPost,
    EncyclopediaEntry,
]


def extract_model_defaults(model_class):
    """Extract all fields with default values from a model."""
    defaults = {}

    # Get all fields from the model
    for field in model_class._meta.get_fields():
        if hasattr(field, "default") and field.default is not None:
            # Skip auto-generated fields
            if field.name in ["id", "path", "depth", "numchild"]:
                continue
            defaults[field.name] = field.default

    return defaults


def main():
    print("Extracting default values from target models...")
    print("=" * 60)

    for model_class in TARGET_MODELS:
        print(f"\n{model_class.__name__}:")
        print("-" * 40)

        defaults = extract_model_defaults(model_class)

        if defaults:
            for field_name, default_value in defaults.items():
                print(f"  {field_name}: {repr(default_value)}")
        else:
            print("  No fields with default values found")


if __name__ == "__main__":
    main()

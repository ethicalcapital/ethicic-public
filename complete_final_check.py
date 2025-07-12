#!/usr/bin/env python
"""
Complete final check to ensure ALL remaining models are CMS manageable.
"""

import os

import django
from django.apps import apps
from django.db import models
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ethicic.settings")
django.setup()


def check_model_editability():
    """Check ALL models for CMS editability - simplified version."""
    public_site_app = apps.get_app_config("public_site")
    page_models = [
        model
        for model in public_site_app.get_models()
        if issubclass(model, Page) and model != Page
    ]

    print("=== COMPLETE CMS EDITABILITY CHECK ===")
    
    models_100_percent = []
    models_needing_work = []

    for model in page_models:
        content_fields = get_content_fields(model)
        hardcoded_fields = get_hardcoded_fields(model, content_fields)
        truly_editable = len(content_fields) - len(hardcoded_fields)
        
        editability = calculate_editability(content_fields, truly_editable)

        if editability == 100:
            models_100_percent.append(
                {"name": model.__name__, "fields": len(content_fields)}
            )
        else:
            models_needing_work.append(create_work_item(
                model.__name__, content_fields, hardcoded_fields, truly_editable, editability
            ))

    display_results(models_100_percent, models_needing_work)
    return models_needing_work


def get_content_fields(model):
    """Get content fields from model."""
    content_fields = []
    page_fields = {f.name for f in Page._meta.fields}

    for field in model._meta.fields:
        if field.name in page_fields:
            continue
        if isinstance(
            field, (models.CharField, models.TextField, RichTextField, StreamField)
        ):
            content_fields.append(field.name)
    return content_fields


def get_hardcoded_fields(model, content_fields):
    """Get fields with hardcoded defaults."""
    hardcoded_fields = []
    for field_name in content_fields:
        field = model._meta.get_field(field_name)
        if hasattr(field, "default") and field.default not in (
            models.NOT_PROVIDED,
            None,
            "",
        ):
            hardcoded_fields.append(field_name)
    return hardcoded_fields


def calculate_editability(content_fields, truly_editable):
    """Calculate editability percentage."""
    return (truly_editable / len(content_fields) * 100) if content_fields else 100


def create_work_item(name, content_fields, hardcoded_fields, truly_editable, editability):
    """Create work item dictionary."""
    return {
        "name": name,
        "total_fields": len(content_fields),
        "hardcoded_fields": len(hardcoded_fields),
        "editable_fields": truly_editable,
        "editability": editability,
        "hardcoded_list": hardcoded_fields[:5],
    }


def display_results(models_100_percent, models_needing_work):
    """Display check results."""
    print(f"✅ MODELS WITH 100% EDITABILITY ({len(models_100_percent)}):")
    models_100_percent.sort(key=lambda x: x["fields"], reverse=True)
    for model_data in models_100_percent:
        print(f"   {model_data['name']} ({model_data['fields']} fields)")

    if models_needing_work:
        print(f"⚠️  MODELS STILL NEEDING WORK ({len(models_needing_work)}):")
        models_needing_work.sort(key=lambda x: x["hardcoded_fields"], reverse=True)
        for model_data in models_needing_work:
            print(f"   {model_data['name']}: {model_data['editability']:.1f}% editable")
    else:
        print("🎉 ALL MODELS ARE 100% EDITABLE!")


if __name__ == "__main__":
    remaining = check_model_editability()

    if remaining:
        print("🎯 NEXT ACTIONS:")
        print(
            f"Fix the remaining {len(remaining)} models to achieve 100% CMS editability"
        )
    else:
        print("🎉 PERFECT! All models are 100% CMS editable!")

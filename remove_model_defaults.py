#!/usr/bin/env python3
"""
Remove all default values from the 13 target models in models.py.
This script performs surgical edits to remove default= parameters while preserving blank=True.
"""

import json
import re
from pathlib import Path

# Load the custom defaults we identified
with open("custom_defaults_backup_20250711_224112.json") as f:
    custom_defaults = json.load(f)

# Target models and their custom default fields
TARGET_MODELS = {
    "StrategyListPage": [
        "intro_text",
        "description",
        "comparison_title",
        "comparison_description",
        "resources_section_title",
        "resources_section_subtitle",
        "resources_section_description",
        "cta_section_title",
        "cta_title",
        "cta_description",
    ],
    "ConsultationPage": [
        "hero_title",
        "hero_subtitle",
        "contact_email",
        "schedule_section_title",
        "schedule_intro_text",
        "alternative_contact_text",
        "expectations_section_title",
        "disclaimer_title",
        "disclaimer_text",
    ],
    "CriteriaPage": [
        "hero_title",
        "hero_subtitle",
        "transparency_section_title",
        "transparency_description",
        "transparency_benefits",
        "github_criteria_url",
        "exclusions_section_title",
        "exclusions_note",
    ],
    "GuidePage": [
        "hero_title",
        "hero_subtitle",
        "description_section_header",
        "download_section_header",
        "resources_section_header",
        "newsletter_section_header",
        "newsletter_description",
    ],
    "FAQIndexPage": [
        "intro_text",
        "description",
        "contact_email",
        "contact_phone",
        "contact_address",
        "meeting_link",
    ],
    "FAQPage": [
        "intro_text",
        "empty_state_title",
        "empty_state_message",
        "empty_state_button_text",
        "empty_state_button_url",
    ],
    "BlogIndexPage": [
        "intro_text",
        "description",
        "featured_title",
        "featured_description",
    ],
    "ResearchPage": [
        "intro_text",
        "description",
        "featured_title",
        "featured_description",
    ],
    "OnboardingPage": [
        "intro_text",
        "form_description",
        "thank_you_title",
        "thank_you_message",
    ],
    "ContactPage": ["intro_text", "email"],
    "EncyclopediaIndexPage": ["intro_text", "description"],
    "BlogPost": ["author", "reading_time"],
    "EncyclopediaEntry": ["difficulty_level"],
}


def remove_default_parameter(field_definition):
    """Remove default= parameter from a field definition while preserving other parameters."""
    # Pattern to match default= parameter with various value types
    patterns = [
        r'default\s*=\s*"[^"]*"',  # String with double quotes
        r"default\s*=\s*'[^']*'",  # String with single quotes
        r'default\s*=\s*"""[^"]*"""',  # Triple-quoted string
        r"default\s*=\s*'''[^']*'''",  # Triple-quoted string with single quotes
        r"default\s*=\s*[^,\)]+",  # Other values (numbers, booleans, etc.)
    ]

    modified = field_definition
    for pattern in patterns:
        modified = re.sub(pattern, "", modified)

    # Clean up any double commas, trailing commas, or comma-space combinations
    modified = re.sub(r",\s*,", ",", modified)  # Remove double commas
    modified = re.sub(
        r",\s*\)", ")", modified
    )  # Remove trailing comma before closing paren
    modified = re.sub(r"\(\s*,", "(", modified)  # Remove comma after opening paren
    modified = re.sub(
        r",\s*\n\s*\)", "\n    )", modified
    )  # Remove trailing comma before closing paren on new line

    return modified


def process_models_file():
    """Process the models.py file to remove default parameters."""
    models_file = Path("public_site/models.py")

    if not models_file.exists():
        print(f"Error: {models_file} not found")
        return None

    print("Processing models.py file...")

    with open(models_file) as f:
        content = f.read()

    # Track modifications
    modifications = []

    # Process each model
    for model_name, field_names in TARGET_MODELS.items():
        print(f"\nProcessing {model_name}...")

        # Find the model class
        model_pattern = rf"class {model_name}\([^)]+\):"
        model_match = re.search(model_pattern, content)

        if not model_match:
            print(f"  Warning: Could not find {model_name} class")
            continue

        model_start = model_match.start()

        # Find the end of the model (next class or end of file)
        next_class_pattern = r"\nclass \w+\([^)]+\):"
        next_class_match = re.search(next_class_pattern, content[model_start + 1 :])

        if next_class_match:
            model_end = model_start + next_class_match.start() + 1
        else:
            model_end = len(content)

        model_content = content[model_start:model_end]
        original_model_content = model_content

        # Process each field that should have its default removed
        for field_name in field_names:
            # Find field definitions with default values
            field_patterns = [
                # Multi-line field definitions
                rf"({field_name}\s*=\s*\w+\([^)]*\n[^)]*default\s*=[^)]*\))",
                # Single-line field definitions
                rf"({field_name}\s*=\s*\w+\([^)]*default\s*=[^)]*\))",
            ]

            for pattern in field_patterns:
                matches = re.finditer(pattern, model_content, re.DOTALL)
                for match in matches:
                    original_field = match.group(1)
                    modified_field = remove_default_parameter(original_field)

                    if original_field != modified_field:
                        model_content = model_content.replace(
                            original_field, modified_field
                        )
                        modifications.append(
                            {
                                "model": model_name,
                                "field": field_name,
                                "original": original_field[:100] + "..."
                                if len(original_field) > 100
                                else original_field,
                                "modified": modified_field[:100] + "..."
                                if len(modified_field) > 100
                                else modified_field,
                            }
                        )
                        print(f"  Modified field: {field_name}")
                        break

        # Replace the model content in the full file
        content = content[:model_start] + model_content + content[model_end:]

    # Save the modified content
    backup_file = models_file.with_suffix(".py.backup")
    with open(backup_file, "w") as f:
        f.write(content)

    print(f"\nOriginal file backed up to: {backup_file}")

    # Show summary of modifications
    print("\nSummary of modifications:")
    print(f"Total modifications made: {len(modifications)}")

    for mod in modifications:
        print(f"  {mod['model']}.{mod['field']}: removed default parameter")

    return content, modifications


def main():
    """Main function to remove default parameters from all target models."""
    print("Removing default parameters from target models...")
    print("=" * 60)

    content, modifications = process_models_file()

    if modifications:
        print(f"\nSuccessfully processed {len(modifications)} field modifications")
        print("Review the changes and then apply them to the actual models.py file")
    else:
        print("No modifications were made - check the patterns and model definitions")

    return content, modifications


if __name__ == "__main__":
    main()

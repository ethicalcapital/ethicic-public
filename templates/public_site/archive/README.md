# Template Archive

This folder contains legacy and unused templates that were moved during the template consolidation on 2025-01-28.

## Archive Structure

### `base_templates/`
Legacy base templates that are no longer used after consolidating everything to use `base_tailwind.html` with Alpine.js theme toggle:

- `base_optimized.html` - Previously used by blog posts, had garden-theme-toggle.js
- `base_production.html` - Production-specific base template
- `base_production_bundles.html` - CSS bundle-optimized base template
- `base_garden_ui_compliant.html` - Garden UI specific base template
- `base.html` - Original base template

### `unused_pages/`
Page templates that were superseded by their `_tailwind.html` versions or are no longer referenced by models:

- `about_page_tailwind.html` - Duplicate, `about_page.html` is used by AboutPage model
- `blog_post_tailwind.html` - Duplicate, consolidated into `blog_post.html`
- `blog_index_tailwind.html` - Duplicate, `blog_index_page.html` is the active template
- `contact_form.html` - Superseded by `contact_form_tailwind.html` (used by models)
- `faq_index.html` - Superseded by `faq_index_tailwind.html` (used by models)
- `faq_page.html` - Superseded by `faq_page_tailwind.html` (used by models)
- `homepage_accessible.html` - Superseded by `homepage_tailwind.html` (used by models)
- `strategy_list.html` - Superseded by `strategy_list_tailwind.html` (used by models)

### `test_debug/`
Development and testing templates:

- `debug_width.html` - Debug template for testing page widths
- `test_clean_nav.html` - Navigation testing template
- `inline_test.html` - Inline styling test template
- `strategy_page_styles.html` - Strategy page styling test template

## Current Active Templates

After consolidation, the site uses:
- **Base Template**: `base_tailwind.html` (Alpine.js theme toggle, Tailwind CSS)
- **Blog Templates**: `blog_base.html` → `blog_post.html` (inherits from base_tailwind.html)
- **All Other Pages**: Inherit directly from `base_tailwind.html`

## Notes

- All active templates now use the unified Alpine.js theme toggle system
- The garden-theme-toggle.js system is no longer needed
- Template inheritance is simplified and consistent across the site
- These archived templates can be safely removed in the future if not needed for reference

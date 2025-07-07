# CMS Editability Report - Ethicic Public Site

## Summary
As of 2025-07-07, a comprehensive audit was performed to ensure all page templates are fully editable through Wagtail CMS.

## ✅ Completed Pages (Fully CMS-Editable)

### 1. **PricingPage**
- Added 30+ fields for all content sections
- Migrated all hardcoded pricing, services, and workshop content
- Used StreamFields for flexible additional services

### 2. **ProcessPage**  
- Added comprehensive fields for screening descriptions
- Implemented StreamFields for product and conduct exclusions
- Migrated all methodology and CTA content

### 3. **AboutPage**
- Added StreamFields for experience timeline
- Added StreamFields for hobbies/interests
- Added featured_posts StreamField
- All previously hardcoded content now editable

### 4. **AdvisorPage**
- Added comprehensive fields for all sections
- Implemented StreamFields for services, benefits, process steps
- Added resource categories with nested resources
- Migrated all hardcoded content

### 5. **LegalPage**
- Already properly configured with all necessary fields

### 6. **CompliancePage**
- Already properly configured with all necessary fields

### 7. **OnboardingPage**
- Already has intro_text field
- Template properly uses richtext filter

### 8. **BlogPost**
- Already fully configured with StreamField content

## ⚠️ Pages with Partial Hardcoded Content

### 1. **InstitutionalPage**
**Has fields for:** Hero content, CTA content
**Still hardcoded:**
- Service cards (4 items)
- Benefits list (6 items)  
- Process steps (4 items)
- Scale metrics (4 items)
- Resource categories and links

### 2. **ConsultationPage**
**Has fields for:** Hero content, introduction
**Still hardcoded:**
- Consultation types (3 items)
- Expectations list (4 items)
- Disclaimer text

### 3. **MediaPage**
**Has fields for:** Intro, media items, press kit
**Still hardcoded:**
- Sidebar content (interview booking, contact info)
- Empty state message

### 4. **FAQPage**
**Has fields for:** Title, intro, FAQ items
**Still hardcoded:**
- Empty state message

### 5. **ContactFormPage**
**Has fields for:** Title, intro, form description
**Still hardcoded:**
- All contact information (email, phone, address, hours)

### 6. **StrategyListPage**
**Has fields for:** Title, intro, strategies
**Still hardcoded:**
- Resource documentation section
- CTA content

### 7. **GuidePage**
**Has fields for:** Title, subtitle, guide content
**Still hardcoded:**
- Section headers
- Resource items

### 8. **PRIDDQPage**
**Has fields for:** All content sections
**Still hardcoded:**
- Section headers only

## 🔧 Recommended Actions

### Priority 1 - High Impact Pages
1. **InstitutionalPage** - Add StreamFields for services, benefits, process, metrics, resources
2. **ContactFormPage** - Add fields for all contact information
3. **ConsultationPage** - Add StreamFields for consultation types and expectations

### Priority 2 - Medium Impact  
4. **MediaPage** - Add fields for sidebar content and empty state
5. **StrategyListPage** - Add StreamField for resources, CTA fields
6. **FAQPage** - Add empty state fields

### Priority 3 - Low Impact
7. **GuidePage** - Add StreamField for resources
8. **PRIDDQPage** - Consider if section headers need to be editable

## Technical Patterns Used

### StreamField Patterns
```python
# For repeating items with multiple fields
services = StreamField([
    ('service', blocks.StructBlock([
        ('title', blocks.CharBlock(max_length=100)),
        ('description', blocks.RichTextBlock()),
    ]))
], blank=True, use_json_field=True)

# For nested categories
resources = StreamField([
    ('category', blocks.StructBlock([
        ('title', blocks.CharBlock(max_length=100)),
        ('items', blocks.ListBlock(blocks.StructBlock([
            ('icon', blocks.CharBlock(max_length=10)),
            ('title', blocks.CharBlock(max_length=100)),
            ('description', blocks.CharBlock(max_length=200)),
            ('url', blocks.URLBlock()),
        ])))
    ]))
], blank=True, use_json_field=True)
```

### Migration Pattern
1. Add fields to model
2. Create migration
3. Create data migration to populate defaults
4. Update template to use model fields
5. Update content_panels for admin UI

## Conclusion

While significant progress has been made with 8 pages fully CMS-editable, there are still 8 pages with varying degrees of hardcoded content. The highest priority should be InstitutionalPage and ContactFormPage as they contain the most business-critical hardcoded content that may need frequent updates.
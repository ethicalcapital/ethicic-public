# Homepage CMS Migration

## Issue
The homepage was displaying content with hardcoded `<strong>` tags that were automatically inserted in the process section, making CMS editing inconsistent with what displayed on the homepage.

## Root Cause
The homepage was using a hardcoded view (`homepage_view.py`) that bypassed the Wagtail CMS system entirely. The content in this view included `<strong>` tags that were not visible or editable in the CMS.

## Solution

### 1. Quick Fix (Completed)
Removed the `<strong>` tags from the hardcoded content in `homepage_view.py`.

### 2. Proper Fix (Completed)
Created a new view `homepage_view_cms.py` that:
- Fetches content from the HomePage model in the CMS
- Falls back to the hardcoded view if there's an error
- Properly integrates with Wagtail's page serving system

### 3. Content Migration (Completed)
- Created management command `update_homepage_content` to sync CMS content
- Updated the HomePage instance in the database to match the hardcoded content (without `<strong>` tags)

## Files Changed

1. **public_site/homepage_view.py** - Removed `<strong>` tags from hardcoded content
2. **public_site/homepage_view_cms.py** - New view that uses CMS content
3. **ethicic/urls.py** - Updated to use the CMS-based view
4. **public_site/management/commands/update_homepage_content.py** - Command to sync content

## How It Works Now

1. The homepage is served from the CMS (HomePage model)
2. Content editors can modify the process step content in the CMS
3. No automatic HTML tags are inserted
4. The content displays exactly as entered in the CMS

## Future Considerations

To fully leverage the CMS:
1. Consider converting the process step fields from `TextField` to `RichTextField` if rich text editing is needed
2. Remove the homepage URL override in `ethicic/urls.py` to let Wagtail handle routing completely
3. Delete the hardcoded `homepage_view.py` once confirmed the CMS version is working correctly

## Testing

To verify the fix:
1. Visit the homepage and check the process section
2. Edit the process step content in the CMS admin
3. Verify changes appear on the frontend without any auto-inserted HTML tags

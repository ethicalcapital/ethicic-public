-- Cleanup placeholder content from the database with proper foreign key handling
-- Run this with: uv run python manage.py dbshell < cleanup_placeholders_proper.sql

-- First, delete from the child tables (specific model tables)

-- Delete placeholder blog posts from public_site_blogpost
DELETE FROM public_site_blogpost 
WHERE page_ptr_id IN (39,40,41,42,43,44,45,46,47,48,49,50,51)
AND (body IS NULL OR body = '' OR LENGTH(body) = 0);

-- Delete duplicate/short FAQ articles from public_site_faqarticle
DELETE FROM public_site_faqarticle 
WHERE page_ptr_id IN (55,56,57,93,94,95)
AND LENGTH(content) < 100;

-- Delete test encyclopedia entries from public_site_encyclopediaentry
DELETE FROM public_site_encyclopediaentry 
WHERE page_ptr_id IN (155,156,157,158,159,160,161,162,163);

-- Now delete from the parent wagtailcore_page table
DELETE FROM wagtailcore_page 
WHERE id IN (39,40,41,42,43,44,45,46,47,48,49,50,51,55,56,57,93,94,95,155,156,157,158,159,160,161,162,163);

-- Show final counts
SELECT 'Blog Posts' as type, COUNT(*) as count FROM public_site_blogpost
UNION ALL
SELECT 'FAQ Articles', COUNT(*) FROM public_site_faqarticle
UNION ALL
SELECT 'Encyclopedia Entries', COUNT(*) FROM public_site_encyclopediaentry;
-- Delete orphaned content from Kinsta that doesn't exist in Ubicloud
-- Run this with: uv run python manage.py dbshell < delete_orphaned_content.sql

-- First, delete from child tables to avoid foreign key constraint errors

-- Delete orphaned blog posts
DELETE FROM public_site_blogpost 
WHERE page_ptr_id IN (360,364,368,369);

-- Delete orphaned FAQ articles
DELETE FROM public_site_faqarticle 
WHERE page_ptr_id IN (21,22,23,19,30,31,32,33,90,91,92,52,53,54,96,111,58,59,112,97,344,98,99,100,102,103,104,105,106,107,108,109,333,113,328,114,346,115,329,330,334,331,332,348,349,335,343,351,352,337,338,339,340,341,342);

-- Delete orphaned encyclopedia entries
DELETE FROM public_site_encyclopediaentry 
WHERE page_ptr_id IN (297,298,299,300,301,302,303,304,305,306,307,308,309,310,311,312,313,314,315,316,317,318,319,320,376);

-- Now delete from the parent wagtailcore_page table
DELETE FROM wagtailcore_page 
WHERE id IN (360,364,368,369,21,22,23,19,30,31,32,33,90,91,92,52,53,54,96,111,58,59,112,97,344,98,99,100,102,103,104,105,106,107,108,109,333,113,328,114,346,115,329,330,334,331,332,348,349,335,343,351,352,337,338,339,340,341,342,297,298,299,300,301,302,303,304,305,306,307,308,309,310,311,312,313,314,315,316,317,318,319,320,376);

-- Show final counts after deletion
SELECT 'Blog Posts' as type, COUNT(*) as count FROM public_site_blogpost
UNION ALL
SELECT 'FAQ Articles', COUNT(*) FROM public_site_faqarticle
UNION ALL
SELECT 'Encyclopedia Entries', COUNT(*) FROM public_site_encyclopediaentry;
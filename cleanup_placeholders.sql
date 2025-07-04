-- Cleanup placeholder content from the database
-- Run this with: uv run python manage.py dbshell < cleanup_placeholders.sql

-- Delete placeholder blog posts (empty body content)
DELETE FROM wagtailcore_page 
WHERE id IN (39,40,41,42,43,44,45,46,47,48,49,50,51)
AND id IN (
    SELECT wp.id 
    FROM wagtailcore_page wp 
    JOIN public_site_blogpost bp ON bp.page_ptr_id = wp.id
    WHERE LENGTH(bp.body) = 0
);

-- Delete duplicate/short FAQ articles
DELETE FROM wagtailcore_page 
WHERE id IN (55,56,57,93,94,95)
AND id IN (
    SELECT wp.id 
    FROM wagtailcore_page wp 
    JOIN public_site_faqarticle fa ON fa.page_ptr_id = wp.id
    WHERE LENGTH(fa.content) < 100
);

-- Delete test encyclopedia entries
DELETE FROM wagtailcore_page 
WHERE id IN (155,156,157,158,159,160,161,162,163)
AND id IN (
    SELECT wp.id 
    FROM wagtailcore_page wp 
    JOIN public_site_encyclopediaentry ee ON ee.page_ptr_id = wp.id
    WHERE wp.title LIKE 'Investment Concept %'
);
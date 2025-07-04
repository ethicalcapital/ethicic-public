#!/usr/bin/env python
"""
Quick WordPress formatting cleanup using direct SQL
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ethicic.settings')
django.setup()

from django.db import connection

def quick_clean():
    print("Quick WordPress formatting cleanup...")
    
    with connection.cursor() as cursor:
        # Clean blog posts
        print("\nCleaning blog posts...")
        cursor.execute("""
            UPDATE public_site_blogpost
            SET body = REGEXP_REPLACE(
                REGEXP_REPLACE(
                    REGEXP_REPLACE(body, '<!-- wp:[^>]+? -->', '', 'g'),
                    '<!-- /wp:[^>]+? -->', '', 'g'
                ),
                '\n\s*\n\s*\n', E'\n\n', 'g'
            )
            WHERE body LIKE '%<!-- wp:%'
        """)
        blog_count = cursor.rowcount
        print(f"  - Cleaned {blog_count} blog posts")
        
        # Clean FAQ articles
        print("\nCleaning FAQ articles...")
        cursor.execute("""
            UPDATE public_site_faqarticle
            SET content = REGEXP_REPLACE(
                REGEXP_REPLACE(
                    REGEXP_REPLACE(content, '<!-- wp:[^>]+? -->', '', 'g'),
                    '<!-- /wp:[^>]+? -->', '', 'g'
                ),
                '\n\s*\n\s*\n', E'\n\n', 'g'
            )
            WHERE content LIKE '%<!-- wp:%'
        """)
        faq_count = cursor.rowcount
        print(f"  - Cleaned {faq_count} FAQ articles")
        
        # Clean encyclopedia entries
        print("\nCleaning encyclopedia entries...")
        cursor.execute("""
            UPDATE public_site_encyclopediaentry
            SET detailed_content = REGEXP_REPLACE(
                REGEXP_REPLACE(
                    REGEXP_REPLACE(detailed_content, '<!-- wp:[^>]+? -->', '', 'g'),
                    '<!-- /wp:[^>]+? -->', '', 'g'
                ),
                '\n\s*\n\s*\n', E'\n\n', 'g'
            )
            WHERE detailed_content LIKE '%<!-- wp:%'
        """)
        encyclopedia_count = cursor.rowcount
        print(f"  - Cleaned {encyclopedia_count} encyclopedia entries")
        
        print(f"\nTotal cleaned: {blog_count + faq_count + encyclopedia_count}")

if __name__ == "__main__":
    quick_clean()
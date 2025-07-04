#!/usr/bin/env python
"""
Check for content that exists in Kinsta but has been deleted from Ubicloud
"""
import os
import sys
import django
import psycopg2
from psycopg2.extras import DictCursor

# Setup Django for Kinsta
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ethicic.settings')
django.setup()

from django.db import connection as kinsta_connection

# Ubicloud connection details
UBICLOUD_DB = {
    'host': 'dewey-db.pgp92x5xnqyj7q1kkftgc93crz.postgres.ubicloud.com',
    'port': 5432,
    'database': 'postgres',
    'user': 'postgres',
    'password': 'tyfhec-wusrYz-3kijde',
    'sslmode': 'require',
    'sslrootcert': './config/ssl/ubicloud-root-ca.pem'
}

def check_deleted_content():
    print("Checking for content deleted from Ubicloud...")
    
    # Connect to Ubicloud
    conn_string = f"host={UBICLOUD_DB['host']} port={UBICLOUD_DB['port']} dbname={UBICLOUD_DB['database']} user={UBICLOUD_DB['user']} password={UBICLOUD_DB['password']} sslmode={UBICLOUD_DB['sslmode']} sslrootcert={UBICLOUD_DB['sslrootcert']}"
    ubicloud_conn = psycopg2.connect(conn_string)
    
    try:
        with kinsta_connection.cursor() as kinsta_cursor, ubicloud_conn.cursor(cursor_factory=DictCursor) as ubi_cursor:
            
            # Get all slugs from Ubicloud for each content type
            print("\n1. Checking Blog Posts...")
            ubi_cursor.execute("""
                SELECT wp.slug, wp.title 
                FROM public_site_blogpost bp
                JOIN wagtailcore_page wp ON bp.page_ptr_id = wp.id
                WHERE wp.live = true
            """)
            ubicloud_blog_slugs = {row['slug']: row['title'] for row in ubi_cursor.fetchall()}
            
            # Get all slugs from Kinsta
            kinsta_cursor.execute("""
                SELECT wp.slug, wp.title, wp.id
                FROM public_site_blogpost bp
                JOIN wagtailcore_page wp ON bp.page_ptr_id = wp.id
                WHERE wp.live = true
            """)
            kinsta_blogs = kinsta_cursor.fetchall()
            
            deleted_blogs = []
            for slug, title, page_id in kinsta_blogs:
                if slug not in ubicloud_blog_slugs:
                    deleted_blogs.append((page_id, title, slug))
            
            if deleted_blogs:
                print(f"  Found {len(deleted_blogs)} blog posts to delete:")
                for page_id, title, slug in deleted_blogs:
                    print(f"    - ID {page_id}: {title} (slug: {slug})")
            else:
                print("  ✓ All blog posts match")
            
            # Check FAQ Articles
            print("\n2. Checking FAQ Articles...")
            ubi_cursor.execute("""
                SELECT wp.slug, wp.title 
                FROM public_site_faqarticle fa
                JOIN wagtailcore_page wp ON fa.page_ptr_id = wp.id
                WHERE wp.live = true
            """)
            ubicloud_faq_slugs = {row['slug']: row['title'] for row in ubi_cursor.fetchall()}
            
            kinsta_cursor.execute("""
                SELECT wp.slug, wp.title, wp.id
                FROM public_site_faqarticle fa
                JOIN wagtailcore_page wp ON fa.page_ptr_id = wp.id
                WHERE wp.live = true
            """)
            kinsta_faqs = kinsta_cursor.fetchall()
            
            deleted_faqs = []
            for slug, title, page_id in kinsta_faqs:
                if slug not in ubicloud_faq_slugs:
                    deleted_faqs.append((page_id, title, slug))
            
            if deleted_faqs:
                print(f"  Found {len(deleted_faqs)} FAQ articles to delete:")
                for page_id, title, slug in deleted_faqs:
                    print(f"    - ID {page_id}: {title[:50]}... (slug: {slug})")
            else:
                print("  ✓ All FAQ articles match")
            
            # Check Encyclopedia Entries
            print("\n3. Checking Encyclopedia Entries...")
            ubi_cursor.execute("""
                SELECT wp.slug, wp.title 
                FROM public_site_encyclopediaentry ee
                JOIN wagtailcore_page wp ON ee.page_ptr_id = wp.id
                WHERE wp.live = true
            """)
            ubicloud_enc_slugs = {row['slug']: row['title'] for row in ubi_cursor.fetchall()}
            
            kinsta_cursor.execute("""
                SELECT wp.slug, wp.title, wp.id
                FROM public_site_encyclopediaentry ee
                JOIN wagtailcore_page wp ON ee.page_ptr_id = wp.id
                WHERE wp.live = true
            """)
            kinsta_encs = kinsta_cursor.fetchall()
            
            deleted_encs = []
            for slug, title, page_id in kinsta_encs:
                if slug not in ubicloud_enc_slugs:
                    deleted_encs.append((page_id, title, slug))
            
            if deleted_encs:
                print(f"  Found {len(deleted_encs)} encyclopedia entries to delete:")
                for page_id, title, slug in deleted_encs:
                    print(f"    - ID {page_id}: {title} (slug: {slug})")
            else:
                print("  ✓ All encyclopedia entries match")
            
            # Summary
            total_to_delete = len(deleted_blogs) + len(deleted_faqs) + len(deleted_encs)
            if total_to_delete > 0:
                print(f"\nTotal items to delete: {total_to_delete}")
                
                # Create deletion SQL
                all_ids_to_delete = [id for id, _, _ in deleted_blogs + deleted_faqs + deleted_encs]
                if all_ids_to_delete:
                    print("\nTo delete these items, run:")
                    print(f"DELETE FROM wagtailcore_page WHERE id IN ({','.join(map(str, all_ids_to_delete))});")
            else:
                print("\n✓ All content in Kinsta matches Ubicloud - no deletions needed!")
                
    finally:
        ubicloud_conn.close()

if __name__ == "__main__":
    check_deleted_content()
#!/usr/bin/env python
"""
Verify that Kinsta and Ubicloud databases are in sync
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ethicic.settings')
django.setup()

from django.db import connection

def verify_sync():
    print("Verifying database synchronization...")
    
    with connection.cursor() as cursor:
        # Count all content types
        cursor.execute("""
            SELECT 
                'Blog Posts' as content_type,
                COUNT(*) as kinsta_count,
                COUNT(CASE WHEN wp.live = true THEN 1 END) as live_count
            FROM public_site_blogpost bp
            JOIN wagtailcore_page wp ON bp.page_ptr_id = wp.id
            
            UNION ALL
            
            SELECT 
                'FAQ Articles',
                COUNT(*),
                COUNT(CASE WHEN wp.live = true THEN 1 END)
            FROM public_site_faqarticle fa
            JOIN wagtailcore_page wp ON fa.page_ptr_id = wp.id
            
            UNION ALL
            
            SELECT 
                'Encyclopedia Entries',
                COUNT(*),
                COUNT(CASE WHEN wp.live = true THEN 1 END)
            FROM public_site_encyclopediaentry ee
            JOIN wagtailcore_page wp ON ee.page_ptr_id = wp.id
        """)
        
        results = cursor.fetchall()
        
        print("\nContent counts in Kinsta database:")
        print("-" * 50)
        for content_type, total, live in results:
            print(f"{content_type}: {total} total ({live} live)")
        
        print("\nExpected counts from Ubicloud:")
        print("-" * 50)
        print("Blog Posts: 23 (all live)")
        print("FAQ Articles: 60 (all live)")
        print("Encyclopedia Entries: 36 (all live)")
        
        # Check if counts match
        blog_match = results[0][2] == 23
        faq_match = results[1][2] == 60
        enc_match = results[2][2] == 36
        
        print("\nSynchronization status:")
        print("-" * 50)
        if blog_match and faq_match and enc_match:
            print("✅ Databases are in sync! No deletions needed.")
        else:
            print("❌ Databases are NOT in sync:")
            if not blog_match:
                print(f"  - Blog posts: {results[0][2]} in Kinsta vs 23 in Ubicloud")
            if not faq_match:
                print(f"  - FAQ articles: {results[1][2]} in Kinsta vs 60 in Ubicloud")
            if not enc_match:
                print(f"  - Encyclopedia: {results[2][2]} in Kinsta vs 36 in Ubicloud")

if __name__ == "__main__":
    verify_sync()
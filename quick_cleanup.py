#!/usr/bin/env python
"""
Quick cleanup of remaining placeholder content
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ethicic.settings')
django.setup()

from django.db import transaction
from wagtail.models import Page

def quick_cleanup():
    print("Quick cleanup of remaining placeholder content...")
    
    # Remaining blog posts
    remaining_blog_ids = [39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51]
    
    # FAQ articles to delete
    faq_ids = [55, 56, 57, 93, 94, 95]
    
    # Encyclopedia test entries
    encyclopedia_ids = [155, 156, 157, 158, 159, 160, 161, 162, 163]
    
    all_ids = remaining_blog_ids + faq_ids + encyclopedia_ids
    
    print(f"Deleting {len(all_ids)} pages in batch...")
    
    with transaction.atomic():
        deleted_count = Page.objects.filter(id__in=all_ids).delete()
        print(f"Deleted: {deleted_count}")
    
    print("Cleanup complete!")

if __name__ == "__main__":
    quick_cleanup()
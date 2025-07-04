#!/usr/bin/env python
"""
Clean up placeholder and test content from the database
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ethicic.settings')
django.setup()

from wagtail.models import Page

def cleanup_content():
    print("Starting cleanup of placeholder content...")
    
    # Blog posts to delete (IDs 16-51 with empty body)
    blog_ids_to_delete = list(range(16, 52))  # 16-51
    
    # FAQ articles to delete (duplicates/short content)
    faq_ids_to_delete = [55, 56, 57, 93, 94, 95]
    
    # Encyclopedia entries to delete (test entries)
    encyclopedia_ids_to_delete = list(range(155, 164))  # 155-163
    
    # Delete blog posts
    print("\nDeleting placeholder blog posts...")
    blog_deleted = 0
    for page_id in blog_ids_to_delete:
        try:
            page = Page.objects.get(id=page_id)
            if hasattr(page, 'blogpost'):
                # Check if it really has empty body
                blog_post = page.blogpost
                if not blog_post.body or len(blog_post.body) == 0:
                    print(f"  - Deleting blog post: {page.title} (ID: {page_id})")
                    page.delete()
                    blog_deleted += 1
                else:
                    print(f"  - Skipping blog post with content: {page.title} (ID: {page_id})")
        except Page.DoesNotExist:
            print(f"  - Page ID {page_id} not found, skipping")
        except Exception as e:
            print(f"  - Error deleting page ID {page_id}: {e}")
    
    # Delete FAQ articles
    print("\nDeleting duplicate/short FAQ articles...")
    faq_deleted = 0
    for page_id in faq_ids_to_delete:
        try:
            page = Page.objects.get(id=page_id)
            if hasattr(page, 'faqarticle'):
                faq = page.faqarticle
                # Check if content is very short (same as summary)
                if len(faq.content) < 100:
                    print(f"  - Deleting FAQ: {page.title[:50]}... (ID: {page_id})")
                    page.delete()
                    faq_deleted += 1
                else:
                    print(f"  - Skipping FAQ with substantial content: {page.title[:50]}... (ID: {page_id})")
        except Page.DoesNotExist:
            print(f"  - Page ID {page_id} not found, skipping")
        except Exception as e:
            print(f"  - Error deleting page ID {page_id}: {e}")
    
    # Delete test encyclopedia entries
    print("\nDeleting test encyclopedia entries...")
    encyclopedia_deleted = 0
    for page_id in encyclopedia_ids_to_delete:
        try:
            page = Page.objects.get(id=page_id)
            if hasattr(page, 'encyclopediaentry'):
                entry = page.encyclopediaentry
                # Check if it's a test entry
                if "Investment Concept" in page.title and len(entry.detailed_content) < 50:
                    print(f"  - Deleting encyclopedia entry: {page.title} (ID: {page_id})")
                    page.delete()
                    encyclopedia_deleted += 1
                else:
                    print(f"  - Skipping encyclopedia entry with real content: {page.title} (ID: {page_id})")
        except Page.DoesNotExist:
            print(f"  - Page ID {page_id} not found, skipping")
        except Exception as e:
            print(f"  - Error deleting page ID {page_id}: {e}")
    
    print("\nCleanup complete!")
    print(f"Blog posts deleted: {blog_deleted}")
    print(f"FAQ articles deleted: {faq_deleted}")
    print(f"Encyclopedia entries deleted: {encyclopedia_deleted}")
    print(f"Total items deleted: {blog_deleted + faq_deleted + encyclopedia_deleted}")

if __name__ == "__main__":
    cleanup_content()
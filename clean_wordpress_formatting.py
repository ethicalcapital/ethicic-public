#!/usr/bin/env python
"""
Clean WordPress formatting from imported content
"""
import os
import django
import re

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ethicic.settings')
django.setup()

from public_site.models import BlogPost, FAQArticle, EncyclopediaEntry
from django.db import transaction

def clean_wordpress_content(content):
    """Remove WordPress block editor comments and clean formatting"""
    if not content:
        return content
    
    # Remove WordPress block comments (<!-- wp:paragraph --> etc.)
    content = re.sub(r'<!-- wp:[^>]+? -->', '', content)
    content = re.sub(r'<!-- /wp:[^>]+? -->', '', content)
    
    # Clean up extra newlines left by comment removal
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    
    # Remove any remaining WordPress shortcodes
    content = re.sub(r'\[/?wp:.*?\]', '', content)
    
    # Trim whitespace
    content = content.strip()
    
    return content

def clean_all_content():
    print("Cleaning WordPress formatting from imported content...")
    
    # Clean blog posts
    print("\nCleaning blog posts...")
    blog_posts = BlogPost.objects.filter(body__contains='<!-- wp:')
    blog_cleaned = 0
    
    with transaction.atomic():
        for post in blog_posts:
            original_length = len(post.body)
            post.body = clean_wordpress_content(post.body)
            new_length = len(post.body)
            
            if post.excerpt:
                post.excerpt = clean_wordpress_content(post.excerpt)
            
            post.save()
            blog_cleaned += 1
            print(f"  - Cleaned: {post.title[:50]}... ({original_length} → {new_length} chars)")
    
    # Clean FAQ articles
    print("\nCleaning FAQ articles...")
    faq_articles = FAQArticle.objects.filter(content__contains='<!-- wp:')
    faq_cleaned = 0
    
    with transaction.atomic():
        for faq in faq_articles:
            original_length = len(faq.content)
            faq.content = clean_wordpress_content(faq.content)
            new_length = len(faq.content)
            
            if faq.summary:
                faq.summary = clean_wordpress_content(faq.summary)
            
            faq.save()
            faq_cleaned += 1
            print(f"  - Cleaned: {faq.title[:50]}... ({original_length} → {new_length} chars)")
    
    # Clean encyclopedia entries
    print("\nCleaning encyclopedia entries...")
    encyclopedia_entries = EncyclopediaEntry.objects.filter(detailed_content__contains='<!-- wp:')
    encyclopedia_cleaned = 0
    
    with transaction.atomic():
        for entry in encyclopedia_entries:
            original_length = len(entry.detailed_content)
            entry.detailed_content = clean_wordpress_content(entry.detailed_content)
            new_length = len(entry.detailed_content)
            
            if entry.summary:
                entry.summary = clean_wordpress_content(entry.summary)
            
            entry.save()
            encyclopedia_cleaned += 1
            print(f"  - Cleaned: {entry.title[:50]}... ({original_length} → {new_length} chars)")
    
    print("\nCleaning complete!")
    print(f"Blog posts cleaned: {blog_cleaned}")
    print(f"FAQ articles cleaned: {faq_cleaned}")
    print(f"Encyclopedia entries cleaned: {encyclopedia_cleaned}")
    print(f"Total cleaned: {blog_cleaned + faq_cleaned + encyclopedia_cleaned}")

if __name__ == "__main__":
    clean_all_content()
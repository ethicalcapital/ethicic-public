#!/usr/bin/env python
import os
import sys
import django
import json
from datetime import datetime
import re

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ethicic.settings')
django.setup()

from django.db import transaction
from wagtail.models import Page
from public_site.models import FAQArticle, EncyclopediaEntry, FAQIndexPage, EncyclopediaIndexPage

def extract_title_from_content(content, default_title):
    """Extract title from content by looking for headers or first sentence"""
    if not content:
        return default_title
    
    # Look for markdown headers
    h1_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if h1_match:
        return h1_match.group(1).strip()
    
    h2_match = re.search(r'^##\s+(.+)$', content, re.MULTILINE)
    if h2_match:
        return h2_match.group(1).strip()
    
    # Look for HTML headers
    html_h1 = re.search(r'<h1[^>]*>(.+?)</h1>', content, re.IGNORECASE)
    if html_h1:
        return re.sub(r'<[^>]+>', '', html_h1.group(1)).strip()
    
    html_h2 = re.search(r'<h2[^>]*>(.+?)</h2>', content, re.IGNORECASE)
    if html_h2:
        return re.sub(r'<[^>]+>', '', html_h2.group(1)).strip()
    
    # Use first sentence
    first_line = content.strip().split('\n')[0]
    if len(first_line) > 10 and len(first_line) < 100:
        return first_line.strip('# ').strip()
    
    return default_title

def bulk_import_faq_articles():
    """Bulk import remaining FAQ articles"""
    print("\n📋 Fast bulk importing remaining FAQ Articles...")
    
    # Get FAQ index page
    faq_index = FAQIndexPage.objects.first()
    if not faq_index:
        print("❌ No FAQ index page found!")
        return 0
    
    # Load fixtures
    try:
        with open('fixtures/public_site_faqarticle.json', 'r') as f:
            faq_data = json.load(f)
    except FileNotFoundError:
        print("❌ FAQ fixtures file not found!")
        return 0
    
    # Get existing FAQ titles to avoid duplicates
    existing_titles = set(FAQArticle.objects.values_list('title', flat=True))
    existing_slugs = set(FAQArticle.objects.values_list('slug', flat=True))
    
    articles_to_create = []
    
    for i, item in enumerate(faq_data):
        fields = item['fields']
        
        # Extract content
        content = fields.get('answer', '') or fields.get('content', '')
        question = fields.get('question', '') or extract_title_from_content(content, f"FAQ Question {i+1}")
        
        # Skip if already exists
        if question[:255] in existing_titles:
            continue
        
        # Generate slug
        slug = re.sub(r'[^a-z0-9]+', '-', question.lower()).strip('-')[:50]
        if not slug:
            slug = f"faq-{i+1}"
        
        # Ensure unique slug
        base_slug = slug
        counter = 1
        while slug in existing_slugs:
            slug = f"{base_slug}-{counter}"
            counter += 1
        existing_slugs.add(slug)
        
        articles_to_create.append({
            'title': question[:255],
            'slug': slug,
            'summary': fields.get('excerpt', '')[:500] or content[:500],
            'content': content,
            'category': fields.get('category', 'general'),
            'priority': fields.get('order', i),
            'featured': fields.get('featured', False),
        })
    
    # Bulk create all articles in one transaction
    created_count = 0
    if articles_to_create:
        try:
            with transaction.atomic():
                for article_data in articles_to_create:
                    faq = FAQArticle(**article_data)
                    faq_index.add_child(instance=faq)
                    faq.save_revision()  # Save revision but don't publish yet
                    created_count += 1
                
                # Bulk publish all at once
                FAQArticle.objects.filter(
                    live=False,
                    path__startswith=faq_index.path
                ).update(live=True)
                
                print(f"✅ Bulk created {created_count} FAQ articles")
        except Exception as e:
            print(f"❌ Error bulk creating FAQs: {e}")
    
    return created_count

def bulk_import_encyclopedia_entries():
    """Bulk import all encyclopedia entries"""
    print("\n📚 Fast bulk importing Encyclopedia Entries...")
    
    # Get encyclopedia index page
    encyclopedia_index = EncyclopediaIndexPage.objects.first()
    if not encyclopedia_index:
        print("❌ No Encyclopedia index page found!")
        return 0
    
    # Load fixtures
    try:
        with open('fixtures/public_site_encyclopediaentry.json', 'r') as f:
            encyclopedia_data = json.load(f)
    except FileNotFoundError:
        print("❌ Encyclopedia fixtures file not found!")
        return 0
    
    # Get existing titles to avoid duplicates
    existing_titles = set(EncyclopediaEntry.objects.values_list('title', flat=True))
    existing_slugs = set(EncyclopediaEntry.objects.values_list('slug', flat=True))
    
    entries_to_create = []
    
    for i, item in enumerate(encyclopedia_data):
        fields = item['fields']
        
        # Extract content
        content = fields.get('content', '') or fields.get('body', '') or fields.get('definition', '')
        title = fields.get('title', '') or fields.get('term', '') or extract_title_from_content(content, f"Encyclopedia Entry {i+1}")
        
        # Skip if already exists
        if title[:255] in existing_titles:
            continue
        
        # Generate slug
        slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')[:50]
        if not slug:
            slug = f"entry-{i+1}"
        
        # Ensure unique slug
        base_slug = slug
        counter = 1
        while slug in existing_slugs:
            slug = f"{base_slug}-{counter}"
            counter += 1
        existing_slugs.add(slug)
        
        entries_to_create.append({
            'title': title[:255],
            'slug': slug,
            'summary': fields.get('definition', '')[:500] or content[:500],
            'detailed_content': content,
            'category': fields.get('category', 'general'),
            'related_terms': ', '.join(fields.get('related_terms', [])) if isinstance(fields.get('related_terms'), list) else fields.get('related_terms', ''),
            'difficulty_level': fields.get('difficulty_level', 'beginner'),
            'examples': fields.get('examples', ''),
            'further_reading': fields.get('further_reading', ''),
        })
    
    # Bulk create all entries in one transaction
    created_count = 0
    if entries_to_create:
        try:
            with transaction.atomic():
                for entry_data in entries_to_create:
                    entry = EncyclopediaEntry(**entry_data)
                    encyclopedia_index.add_child(instance=entry)
                    entry.save_revision()  # Save revision but don't publish yet
                    created_count += 1
                
                # Bulk publish all at once
                EncyclopediaEntry.objects.filter(
                    live=False,
                    path__startswith=encyclopedia_index.path
                ).update(live=True)
                
                print(f"✅ Bulk created {created_count} Encyclopedia entries")
        except Exception as e:
            print(f"❌ Error bulk creating Encyclopedia entries: {e}")
    
    return created_count

def main():
    """Main import function"""
    print("🚀 Starting Fast Bulk Content Import...")
    
    # Check current status
    from public_site.models import BlogPost
    
    blog_count = BlogPost.objects.count()
    faq_count = FAQArticle.objects.count()
    encyclopedia_count = EncyclopediaEntry.objects.count()
    
    print(f"\n📊 Current Status:")
    print(f"  - Blog Posts: {blog_count}/20")
    print(f"  - FAQ Articles: {faq_count}/41")
    print(f"  - Encyclopedia Entries: {encyclopedia_count}/34")
    
    # Only import what's missing
    faq_imported = 0
    encyclopedia_imported = 0
    
    if faq_count < 41:
        faq_imported = bulk_import_faq_articles()
    
    if encyclopedia_count < 34:
        encyclopedia_imported = bulk_import_encyclopedia_entries()
    
    # Final status
    final_blog = BlogPost.objects.count()
    final_faq = FAQArticle.objects.count()
    final_encyclopedia = EncyclopediaEntry.objects.count()
    
    total_items = final_blog + final_faq + final_encyclopedia
    total_expected = 95
    
    print(f"\n🎯 Final Import Status:")
    print(f"  - Blog Posts: {final_blog}/20 ({final_blog/20*100:.0f}%)")
    print(f"  - FAQ Articles: {final_faq}/41 ({final_faq/41*100:.0f}%)")
    print(f"  - Encyclopedia Entries: {final_encyclopedia}/34 ({final_encyclopedia/34*100:.0f}%)")
    print(f"  - TOTAL: {total_items}/{total_expected} ({total_items/total_expected*100:.1f}%)")
    
    if total_items == total_expected:
        print("\n✅ 🎉 100% COMPLETE! All content successfully imported!")
    else:
        print(f"\n⚠️  {total_expected - total_items} items still missing")

if __name__ == "__main__":
    main()
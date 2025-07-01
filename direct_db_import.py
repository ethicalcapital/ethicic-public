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

from django.db import connection, transaction
from django.contrib.contenttypes.models import ContentType
from wagtail.models import Page
from public_site.models import FAQArticle, EncyclopediaEntry, FAQIndexPage, EncyclopediaIndexPage

def extract_title_from_content(content, default_title):
    """Extract title from content"""
    if not content:
        return default_title
    
    # Look for headers or use first line
    for pattern in [r'^#\s+(.+)$', r'^##\s+(.+)$', r'<h[12][^>]*>(.+?)</h[12]>']:
        match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
        if match:
            return re.sub(r'<[^>]+>', '', match.group(1)).strip()
    
    first_line = content.strip().split('\n')[0][:100]
    return first_line.strip('# ').strip() if len(first_line) > 10 else default_title

def direct_import_remaining_content():
    """Direct database import of remaining content"""
    print("🚀 Starting Direct Database Import...")
    
    # Get index pages
    faq_index = FAQIndexPage.objects.first()
    encyclopedia_index = EncyclopediaIndexPage.objects.first()
    
    if not faq_index or not encyclopedia_index:
        print("❌ Missing index pages!")
        return
    
    # Get content types
    faq_ct = ContentType.objects.get_for_model(FAQArticle)
    encyclopedia_ct = ContentType.objects.get_for_model(EncyclopediaEntry)
    
    # Track existing content
    existing_faq_titles = set(FAQArticle.objects.values_list('title', flat=True))
    existing_encyclopedia_titles = set(EncyclopediaEntry.objects.values_list('title', flat=True))
    
    # Import FAQ Articles
    print("\n📋 Importing remaining FAQ Articles...")
    try:
        with open('fixtures/public_site_faqarticle.json', 'r') as f:
            faq_data = json.load(f)
        
        faq_count = 0
        with transaction.atomic():
            for i, item in enumerate(faq_data):
                fields = item['fields']
                content = fields.get('answer', '') or fields.get('content', '')
                question = fields.get('question', '') or extract_title_from_content(content, f"FAQ Question {i+1}")
                
                if question[:255] in existing_faq_titles:
                    continue
                
                slug = re.sub(r'[^a-z0-9]+', '-', question.lower()).strip('-')[:50] or f"faq-{i+1}"
                
                # Ensure unique slug by adding suffix if needed
                slug_base = slug
                counter = 1
                while Page.objects.filter(slug=slug, path__startswith=faq_index.path).exists():
                    slug = f"{slug_base}-{counter}"
                    counter += 1
                
                # Create page directly
                with connection.cursor() as cursor:
                    # Get next available path
                    cursor.execute("""
                        SELECT MAX(path) FROM wagtailcore_page 
                        WHERE path LIKE %s AND length(path) = %s
                    """, [faq_index.path + '%', len(faq_index.path) + 4])
                    
                    last_path = cursor.fetchone()[0]
                    if last_path:
                        # Extract the last 4 chars and increment
                        last_num = int(last_path[-4:], 36)
                        next_num = format(last_num + 1, '04X').lower()
                    else:
                        next_num = '0001'
                    
                    new_path = faq_index.path + next_num
                    
                    # Insert into wagtailcore_page
                    cursor.execute("""
                        INSERT INTO wagtailcore_page (
                            path, depth, numchild, title, slug, 
                            content_type_id, live, has_unpublished_changes, 
                            url_path, seo_title, show_in_menus, search_description,
                            first_published_at, last_published_at, latest_revision_created_at,
                            live_revision_id, locale_id, translation_key, alias_of_id,
                            locked, locked_at, locked_by_id, owner_id
                        ) VALUES (
                            %s, %s, 0, %s, %s,
                            %s, true, false,
                            %s, '', false, '',
                            NOW(), NOW(), NOW(),
                            NULL, 1, gen_random_uuid(), NULL,
                            false, NULL, NULL, NULL
                        ) RETURNING id
                    """, [
                        new_path,
                        faq_index.depth + 1,
                        question[:255],
                        slug,
                        faq_ct.id,
                        faq_index.url_path + slug + '/'
                    ])
                    
                    page_id = cursor.fetchone()[0]
                    
                    # Insert into public_site_faqarticle
                    cursor.execute("""
                        INSERT INTO public_site_faqarticle (
                            page_ptr_id, summary, content, category, 
                            priority, featured, related_articles, keywords
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, [
                        page_id,
                        fields.get('excerpt', '')[:500] or content[:500],
                        content,
                        fields.get('category', 'general'),
                        fields.get('order', i),
                        fields.get('featured', False),
                        '',
                        ''
                    ])
                    
                    # Update parent's numchild
                    cursor.execute("""
                        UPDATE wagtailcore_page 
                        SET numchild = numchild + 1 
                        WHERE id = %s
                    """, [faq_index.id])
                    
                    faq_count += 1
        
        print(f"✅ Imported {faq_count} FAQ articles")
    except Exception as e:
        print(f"❌ Error importing FAQs: {e}")
    
    # Import Encyclopedia Entries
    print("\n📚 Importing Encyclopedia Entries...")
    try:
        with open('fixtures/public_site_encyclopediaentry.json', 'r') as f:
            encyclopedia_data = json.load(f)
        
        encyclopedia_count = 0
        with transaction.atomic():
            for i, item in enumerate(encyclopedia_data):
                fields = item['fields']
                content = fields.get('content', '') or fields.get('body', '') or fields.get('definition', '')
                title = fields.get('title', '') or fields.get('term', '') or extract_title_from_content(content, f"Entry {i+1}")
                
                if title[:255] in existing_encyclopedia_titles:
                    continue
                
                slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')[:50] or f"entry-{i+1}"
                
                # Ensure unique slug
                slug_base = slug
                counter = 1
                while Page.objects.filter(slug=slug, path__startswith=encyclopedia_index.path).exists():
                    slug = f"{slug_base}-{counter}"
                    counter += 1
                
                # Create page directly
                with connection.cursor() as cursor:
                    # Get next available path
                    cursor.execute("""
                        SELECT MAX(path) FROM wagtailcore_page 
                        WHERE path LIKE %s AND length(path) = %s
                    """, [encyclopedia_index.path + '%', len(encyclopedia_index.path) + 4])
                    
                    last_path = cursor.fetchone()[0]
                    if last_path:
                        last_num = int(last_path[-4:], 36)
                        next_num = format(last_num + 1, '04X').lower()
                    else:
                        next_num = '0001'
                    
                    new_path = encyclopedia_index.path + next_num
                    
                    # Insert into wagtailcore_page
                    cursor.execute("""
                        INSERT INTO wagtailcore_page (
                            path, depth, numchild, title, slug, 
                            content_type_id, live, has_unpublished_changes, 
                            url_path, seo_title, show_in_menus, search_description,
                            first_published_at, last_published_at, latest_revision_created_at,
                            live_revision_id, locale_id, translation_key, alias_of_id,
                            locked, locked_at, locked_by_id, owner_id
                        ) VALUES (
                            %s, %s, 0, %s, %s,
                            %s, true, false,
                            %s, '', false, '',
                            NOW(), NOW(), NOW(),
                            NULL, 1, gen_random_uuid(), NULL,
                            false, NULL, NULL, NULL
                        ) RETURNING id
                    """, [
                        new_path,
                        encyclopedia_index.depth + 1,
                        title[:255],
                        slug,
                        encyclopedia_ct.id,
                        encyclopedia_index.url_path + slug + '/'
                    ])
                    
                    page_id = cursor.fetchone()[0]
                    
                    # Insert into public_site_encyclopediaentry
                    cursor.execute("""
                        INSERT INTO public_site_encyclopediaentry (
                            page_ptr_id, summary, detailed_content, category,
                            related_terms, difficulty_level, examples, further_reading
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, [
                        page_id,
                        fields.get('definition', '')[:500] or content[:500],
                        content,
                        fields.get('category', 'general'),
                        ', '.join(fields.get('related_terms', [])) if isinstance(fields.get('related_terms'), list) else fields.get('related_terms', ''),
                        fields.get('difficulty_level', 'beginner'),
                        fields.get('examples', ''),
                        fields.get('further_reading', '')
                    ])
                    
                    # Update parent's numchild
                    cursor.execute("""
                        UPDATE wagtailcore_page 
                        SET numchild = numchild + 1 
                        WHERE id = %s
                    """, [encyclopedia_index.id])
                    
                    encyclopedia_count += 1
        
        print(f"✅ Imported {encyclopedia_count} Encyclopedia entries")
    except Exception as e:
        print(f"❌ Error importing Encyclopedia entries: {e}")
    
    # Final status
    from public_site.models import BlogPost
    
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

if __name__ == "__main__":
    direct_import_remaining_content()
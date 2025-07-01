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

from django.db import transaction, connection
from wagtail.models import Page, Site
from public_site.models import BlogPost, FAQArticle, EncyclopediaEntry, BlogIndexPage, FAQIndexPage, EncyclopediaIndexPage, HomePage

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

def ensure_index_pages():
    """Ensure all index pages exist"""
    print("\n🔧 Ensuring index pages exist...")
    
    # Get home page
    home = HomePage.objects.first()
    if not home:
        print("❌ No home page found!")
        return False
    
    # Handle FAQ Index Page
    faq_index = FAQIndexPage.objects.first()
    if not faq_index:
        # Check if there's an existing page with slug 'faq'
        existing_faq = Page.objects.filter(slug='faq').first()
        if existing_faq:
            print(f"Converting existing FAQ page (id: {existing_faq.id}) to FAQIndexPage...")
            with connection.cursor() as cursor:
                # First create the FAQIndexPage record with all fields
                cursor.execute("""
                    INSERT INTO public_site_faqindexpage (
                        page_ptr_id, 
                        intro_text, 
                        description,
                        contact_email,
                        contact_phone,
                        contact_address,
                        contact_hours
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (page_ptr_id) DO UPDATE SET
                        intro_text = EXCLUDED.intro_text,
                        description = EXCLUDED.description
                """, [
                    existing_faq.id,
                    '<p>Find answers to frequently asked questions about Ethical Capital Investment Collaborative.</p>',
                    '<p>Our comprehensive FAQ section provides detailed answers to help you understand our investment approach, account management, and ethical screening process.</p>',
                    'hello@ethicic.com',
                    '+1 347 625 9000',
                    '90 N 400 E, Provo, UT, 84606',
                    '8:00 AM - 5:00 PM MT, Monday - Friday'
                ])
                
                # Update content_type
                cursor.execute("""
                    UPDATE wagtailcore_page 
                    SET content_type_id = (
                        SELECT id FROM django_content_type 
                        WHERE app_label = 'public_site' AND model = 'faqindexpage'
                    )
                    WHERE id = %s
                """, [existing_faq.id])
            
            faq_index = FAQIndexPage.objects.get(id=existing_faq.id)
            print("✅ Converted existing FAQ page to FAQIndexPage")
        else:
            print("Creating new FAQ Index Page...")
            faq_index = FAQIndexPage(
                title="FAQ",
                slug="faq",
                intro_text="<p>Find answers to frequently asked questions about Ethical Capital Investment Collaborative.</p>"
            )
            home.add_child(instance=faq_index)
            faq_index.save_revision().publish()
            print("✅ Created FAQ Index Page")
    
    # Handle Encyclopedia Index Page  
    encyclopedia_index = EncyclopediaIndexPage.objects.first()
    if not encyclopedia_index:
        # Check if there's an existing page with slug 'encyclopedia'
        existing_encyclopedia = Page.objects.filter(slug='encyclopedia').first()
        if existing_encyclopedia:
            print(f"Converting existing Encyclopedia page (id: {existing_encyclopedia.id}) to EncyclopediaIndexPage...")
            with connection.cursor() as cursor:
                # First create the EncyclopediaIndexPage record
                cursor.execute("""
                    INSERT INTO public_site_encyclopediaindexpage (
                        page_ptr_id,
                        intro_text,
                        search_prompt
                    )
                    VALUES (%s, %s, %s)
                    ON CONFLICT (page_ptr_id) DO UPDATE SET
                        intro_text = EXCLUDED.intro_text
                """, [
                    existing_encyclopedia.id,
                    '<p>Explore our comprehensive guide to investment terms and concepts.</p>',
                    'Search for investment terms and concepts...'
                ])
                
                # Update content_type
                cursor.execute("""
                    UPDATE wagtailcore_page 
                    SET content_type_id = (
                        SELECT id FROM django_content_type 
                        WHERE app_label = 'public_site' AND model = 'encyclopediaindexpage'
                    )
                    WHERE id = %s
                """, [existing_encyclopedia.id])
            
            encyclopedia_index = EncyclopediaIndexPage.objects.get(id=existing_encyclopedia.id)
            print("✅ Converted existing Encyclopedia page to EncyclopediaIndexPage")
        else:
            print("Creating new Encyclopedia Index Page...")
            encyclopedia_index = EncyclopediaIndexPage(
                title="Investment Encyclopedia",
                slug="encyclopedia",
                intro_text="<p>Explore our comprehensive guide to investment terms and concepts.</p>"
            )
            home.add_child(instance=encyclopedia_index)
            encyclopedia_index.save_revision().publish()
            print("✅ Created Encyclopedia Index Page")
    
    return True

def import_faq_articles():
    """Import all FAQ articles from fixtures"""
    print("\n📋 Importing FAQ Articles...")
    
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
    
    created_count = 0
    skipped_count = 0
    existing_slugs = set(FAQArticle.objects.values_list('slug', flat=True))
    
    for i, item in enumerate(faq_data):
        fields = item['fields']
        
        # Extract content - FAQArticle uses 'content' field (RichTextField)
        content = fields.get('answer', '') or fields.get('content', '')
        question = fields.get('question', '') or extract_title_from_content(content, f"FAQ Question {i+1}")
        
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
        
        # Check if this article already exists by title
        if FAQArticle.objects.filter(title=question[:255]).exists():
            skipped_count += 1
            continue
        
        try:
            with transaction.atomic():
                faq = FAQArticle(
                    title=question[:255],
                    slug=slug,
                    summary=fields.get('excerpt', '')[:500] or content[:500],
                    content=content,  # RichTextField, not StreamField
                    category=fields.get('category', 'general'),
                    priority=fields.get('order', i),
                    featured=fields.get('featured', False),
                )
                faq_index.add_child(instance=faq)
                faq.save_revision().publish()
                created_count += 1
                print(f"✅ Created FAQ: {question[:60]}...")
        except Exception as e:
            print(f"❌ Error creating FAQ {i+1}: {e}")
    
    print(f"\n✅ FAQ Import Complete: {created_count} created, {skipped_count} skipped")
    return created_count

def import_encyclopedia_entries():
    """Import all encyclopedia entries from fixtures"""
    print("\n📚 Importing Encyclopedia Entries...")
    
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
    
    created_count = 0
    skipped_count = 0
    existing_slugs = set(EncyclopediaEntry.objects.values_list('slug', flat=True))
    
    for i, item in enumerate(encyclopedia_data):
        fields = item['fields']
        
        # Extract content - EncyclopediaEntry uses 'detailed_content' field
        content = fields.get('content', '') or fields.get('body', '') or fields.get('definition', '')
        title = fields.get('title', '') or fields.get('term', '') or extract_title_from_content(content, f"Encyclopedia Entry {i+1}")
        
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
        
        # Check if this entry already exists by title
        if EncyclopediaEntry.objects.filter(title=title[:255]).exists():
            skipped_count += 1
            continue
        
        try:
            with transaction.atomic():
                entry = EncyclopediaEntry(
                    title=title[:255],
                    slug=slug,
                    summary=fields.get('definition', '')[:500] or content[:500],
                    detailed_content=content,  # RichTextField
                    category=fields.get('category', 'general'),
                    related_terms=', '.join(fields.get('related_terms', [])) if isinstance(fields.get('related_terms'), list) else fields.get('related_terms', ''),
                    difficulty_level=fields.get('difficulty_level', 'beginner'),
                    examples=fields.get('examples', ''),
                    further_reading=fields.get('further_reading', ''),
                )
                encyclopedia_index.add_child(instance=entry)
                entry.save_revision().publish()
                created_count += 1
                print(f"✅ Created Encyclopedia Entry: {title[:60]}...")
        except Exception as e:
            print(f"❌ Error creating Encyclopedia Entry {i+1}: {e}")
    
    print(f"\n✅ Encyclopedia Import Complete: {created_count} created, {skipped_count} skipped")
    return created_count

def main():
    """Main import function"""
    print("🚀 Starting Comprehensive Content Import...")
    
    # Ensure index pages exist
    if not ensure_index_pages():
        print("❌ Failed to create index pages")
        return
    
    # Check current status
    blog_count = BlogPost.objects.count()
    faq_count = FAQArticle.objects.count()
    encyclopedia_count = EncyclopediaEntry.objects.count()
    
    print(f"\n📊 Current Status:")
    print(f"  - Blog Posts: {blog_count}/20")
    print(f"  - FAQ Articles: {faq_count}/41")
    print(f"  - Encyclopedia Entries: {encyclopedia_count}/34")
    
    # Import missing content
    faq_imported = import_faq_articles()
    encyclopedia_imported = import_encyclopedia_entries()
    
    # Final status
    final_blog = BlogPost.objects.count()
    final_faq = FAQArticle.objects.count()
    final_encyclopedia = EncyclopediaEntry.objects.count()
    
    total_items = final_blog + final_faq + final_encyclopedia
    total_expected = 20 + 41 + 34  # 95 total
    
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
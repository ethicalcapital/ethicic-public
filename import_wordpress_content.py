#!/usr/bin/env python
"""
Import WordPress content into Django/Wagtail database
"""
import os
import sys
import django
import xml.etree.ElementTree as ET
from datetime import datetime
from html import unescape
import re

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ethicic.settings')
django.setup()

from django.utils.text import slugify
from django.utils import timezone
from wagtail.models import Page
from public_site.models import BlogPost, BlogIndexPage, FAQArticle, FAQIndexPage, EncyclopediaEntry, EncyclopediaIndexPage

def clean_content(content):
    """Clean and format content from WordPress"""
    if not content:
        return ""
    
    # Unescape HTML entities
    content = unescape(content)
    
    # Convert WordPress shortcodes to HTML
    content = re.sub(r'\[/?wp:.*?\]', '', content)
    
    # Clean up extra whitespace
    content = re.sub(r'\n\s*\n', '\n\n', content)
    
    return content.strip()

def parse_wordpress_date(date_str):
    """Parse WordPress date format to Django datetime"""
    if not date_str:
        return None
    try:
        # WordPress format: "Wed, 01 Jan 2020 12:00:00 +0000"
        dt = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z")
        return dt
    except:
        return None

def import_content():
    print("Starting WordPress content import...")
    
    # Parse XML file
    tree = ET.parse('/Users/srvo/ethicic-public/wordpress-export.xml')
    root = tree.getroot()
    
    # Define namespaces
    namespaces = {
        'wp': 'http://wordpress.org/export/1.2/',
        'content': 'http://purl.org/rss/1.0/modules/content/',
        'excerpt': 'http://wordpress.org/export/1.2/excerpt/',
        'dc': 'http://purl.org/dc/elements/1.1/'
    }
    
    # Get channel
    channel = root.find('channel')
    
    # Find parent pages
    blog_index = BlogIndexPage.objects.first()
    faq_index = FAQIndexPage.objects.first()
    encyclopedia_index = EncyclopediaIndexPage.objects.first()
    
    if not blog_index:
        print("ERROR: No BlogIndexPage found!")
        return
    if not faq_index:
        print("ERROR: No FAQIndexPage found!")
        return
    if not encyclopedia_index:
        print("ERROR: No EncyclopediaIndexPage found!")
        return
    
    # Process all items
    posts_imported = 0
    faqs_imported = 0
    encyclopedia_imported = 0
    
    # First, import glossary terms as encyclopedia entries
    print("\nImporting glossary terms as encyclopedia entries...")
    for term in channel.findall('wp:term', namespaces):
        taxonomy = term.find('wp:term_taxonomy', namespaces)
        if taxonomy is not None and taxonomy.text == 'glossaries':
            term_name = term.find('wp:term_name', namespaces).text
            term_slug = term.find('wp:term_slug', namespaces).text
            term_desc_elem = term.find('wp:term_description', namespaces)
            term_desc = clean_content(term_desc_elem.text if term_desc_elem is not None else "")
            
            if not term_desc:
                print(f"  - Skipping glossary term with no description: {term_name}")
                continue
                
            print(f"Importing glossary term: {term_name}")
            
            # Check if already exists
            if EncyclopediaEntry.objects.filter(slug=term_slug).exists():
                print(f"  - Skipping, already exists: {term_slug}")
                continue
            
            try:
                # Extract first paragraph as summary
                summary = term_desc.split('\n')[0][:500] if term_desc else ""
                
                encyclopedia = EncyclopediaEntry(
                    title=term_name,
                    slug=term_slug,
                    summary=summary,
                    detailed_content=term_desc,
                    category="general",  # Use a valid category from the model choices
                    live=True,
                    first_published_at=timezone.now()
                )
                encyclopedia_index.add_child(instance=encyclopedia)
                encyclopedia.save_revision().publish()
                encyclopedia_imported += 1
                print(f"  - Successfully imported glossary term: {term_name}")
            except Exception as e:
                print(f"  - ERROR importing glossary term {term_name}: {e}")
    
    print(f"\nProcessing posts...")
    
    for item in channel.findall('item'):
        # Get basic info
        title = item.find('title').text
        post_type = item.find('wp:post_type', namespaces).text
        status = item.find('wp:status', namespaces).text
        
        # Skip if not published
        if status != 'publish':
            continue
            
        # Get content
        content_elem = item.find('content:encoded', namespaces)
        content = clean_content(content_elem.text if content_elem is not None else "")
        
        # Get excerpt
        excerpt_elem = item.find('excerpt:encoded', namespaces)
        excerpt = clean_content(excerpt_elem.text if excerpt_elem is not None else "")
        
        # Get dates
        pub_date_str = item.find('pubDate').text
        pub_date = parse_wordpress_date(pub_date_str)
        
        # Get slug
        post_name = item.find('wp:post_name', namespaces).text
        slug = post_name or slugify(title)[:50]
        
        if post_type == 'post':
            # Import as BlogPost
            print(f"Importing blog post: {title}")
            
            # Check if already exists
            if BlogPost.objects.filter(slug=slug).exists():
                print(f"  - Skipping, already exists: {slug}")
                continue
            
            try:
                blog_post = BlogPost(
                    title=title[:255],
                    slug=slug,
                    excerpt=excerpt[:300] if excerpt else "",
                    body=content,
                    live=True,
                    first_published_at=pub_date or timezone.now()
                )
                blog_index.add_child(instance=blog_post)
                blog_post.save_revision().publish()
                posts_imported += 1
                print(f"  - Successfully imported: {title}")
            except Exception as e:
                print(f"  - ERROR importing {title}: {e}")
                
        elif post_type == 'docs':
            # Check if this doc has glossary categories
            has_glossary = False
            categories = item.findall('category')
            for cat in categories:
                if cat.get('domain') == 'glossaries':
                    has_glossary = True
                    break
            
            if has_glossary:
                # Import as EncyclopediaEntry
                print(f"Importing encyclopedia entry: {title}")
                
                # Check if already exists
                if EncyclopediaEntry.objects.filter(slug=slug).exists():
                    print(f"  - Skipping, already exists: {slug}")
                    continue
                
                try:
                    encyclopedia = EncyclopediaEntry(
                        title=title[:255],
                        slug=slug,
                        summary=excerpt[:500] if excerpt else "",
                        detailed_content=content,
                        category="general",  # Use a valid category from the model choices
                        live=True,
                        first_published_at=pub_date or timezone.now()
                    )
                    encyclopedia_index.add_child(instance=encyclopedia)
                    encyclopedia.save_revision().publish()
                    encyclopedia_imported += 1
                    print(f"  - Successfully imported as encyclopedia: {title}")
                except Exception as e:
                    print(f"  - ERROR importing encyclopedia {title}: {e}")
            else:
                # Import as FAQArticle
                print(f"Importing FAQ/doc: {title}")
                
                # Check if already exists
                if FAQArticle.objects.filter(slug=slug).exists():
                    print(f"  - Skipping, already exists: {slug}")
                    continue
                    
                try:
                    faq = FAQArticle(
                        title=title[:255],
                        slug=slug,
                        summary=excerpt[:500] if excerpt else title[:500],
                        content=content,
                        category="general",  # Default category
                        live=True,
                        first_published_at=pub_date or timezone.now()
                    )
                    faq_index.add_child(instance=faq)
                    faq.save_revision().publish()
                    faqs_imported += 1
                    print(f"  - Successfully imported: {title}")
                except Exception as e:
                    print(f"  - ERROR importing {title}: {e}")
    
    print(f"\nImport complete!")
    print(f"Blog posts imported: {posts_imported}")
    print(f"FAQ articles imported: {faqs_imported}")
    print(f"Encyclopedia entries imported: {encyclopedia_imported}")

if __name__ == "__main__":
    import_content()
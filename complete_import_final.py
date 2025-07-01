#!/usr/bin/env python
import os
import sys
import django
import json
import re

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ethicic.settings')
django.setup()

from django.db import transaction
from public_site.models import BlogPost, FAQArticle, EncyclopediaEntry, FAQIndexPage, EncyclopediaIndexPage

def extract_title_from_content(content, default_title):
    """Extract title from content"""
    if not content:
        return default_title
    
    # Simple extraction
    first_line = content.strip().split('\n')[0][:100]
    if len(first_line) > 10:
        return re.sub(r'<[^>]+>', '', first_line).strip('# ')
    return default_title

def main():
    print("🚀 Completing Content Import...")
    
    # Check current status
    blog_count = BlogPost.objects.count()
    faq_count = FAQArticle.objects.count()
    encyclopedia_count = EncyclopediaEntry.objects.count()
    
    total_current = blog_count + faq_count + encyclopedia_count
    total_expected = 95
    
    print(f"\n📊 Current Status: {total_current}/{total_expected} ({total_current/total_expected*100:.1f}%)")
    print(f"  - Blog Posts: {blog_count}/20")
    print(f"  - FAQ Articles: {faq_count}/41") 
    print(f"  - Encyclopedia Entries: {encyclopedia_count}/34")
    
    # If already complete, exit
    if total_current >= total_expected:
        print("\n✅ 🎉 100% COMPLETE! All content imported!")
        return
    
    # Import remaining FAQs
    if faq_count < 41:
        print(f"\n📋 Need to import {41 - faq_count} more FAQ articles...")
        faq_index = FAQIndexPage.objects.first()
        
        if faq_index:
            try:
                with open('fixtures/public_site_faqarticle.json', 'r') as f:
                    faq_data = json.load(f)
                
                existing_titles = set(FAQArticle.objects.values_list('title', flat=True))
                imported = 0
                
                # Process in batches of 5
                for i, item in enumerate(faq_data):
                    if imported >= 5:  # Limit batch size
                        break
                        
                    fields = item['fields']
                    content = fields.get('answer', '') or fields.get('content', '')
                    question = fields.get('question', '') or extract_title_from_content(content, f"FAQ {i+1}")
                    
                    if question[:255] in existing_titles:
                        continue
                    
                    slug = re.sub(r'[^a-z0-9]+', '-', question.lower()).strip('-')[:40] or f"faq-{i+1}"
                    
                    # Ensure unique slug
                    if FAQArticle.objects.filter(slug=slug).exists():
                        slug = f"{slug}-{i}"
                    
                    try:
                        with transaction.atomic():
                            faq = FAQArticle(
                                title=question[:255],
                                slug=slug,
                                summary=content[:500],
                                content=content,
                                category=fields.get('category', 'general'),
                                priority=i,
                                featured=False,
                            )
                            faq_index.add_child(instance=faq)
                            faq.save_revision().publish()
                            imported += 1
                            print(f"  ✅ Imported FAQ: {question[:50]}...")
                    except Exception as e:
                        print(f"  ❌ Error: {e}")
                
                print(f"  Imported {imported} FAQ articles in this batch")
                
            except Exception as e:
                print(f"  ❌ Error loading FAQs: {e}")
    
    # Import remaining Encyclopedia entries
    if encyclopedia_count < 34:
        print(f"\n📚 Need to import {34 - encyclopedia_count} Encyclopedia entries...")
        encyclopedia_index = EncyclopediaIndexPage.objects.first()
        
        if encyclopedia_index:
            try:
                with open('fixtures/public_site_encyclopediaentry.json', 'r') as f:
                    encyclopedia_data = json.load(f)
                
                existing_titles = set(EncyclopediaEntry.objects.values_list('title', flat=True))
                imported = 0
                
                # Process in batches of 5
                for i, item in enumerate(encyclopedia_data):
                    if imported >= 5:  # Limit batch size
                        break
                        
                    fields = item['fields']
                    content = fields.get('content', '') or fields.get('body', '')
                    title = fields.get('title', '') or fields.get('term', '') or extract_title_from_content(content, f"Entry {i+1}")
                    
                    if title[:255] in existing_titles:
                        continue
                    
                    slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')[:40] or f"entry-{i+1}"
                    
                    # Ensure unique slug
                    if EncyclopediaEntry.objects.filter(slug=slug).exists():
                        slug = f"{slug}-{i}"
                    
                    try:
                        with transaction.atomic():
                            entry = EncyclopediaEntry(
                                title=title[:255],
                                slug=slug,
                                summary=content[:500],
                                detailed_content=content,
                                category=fields.get('category', 'general'),
                                difficulty_level='beginner',
                            )
                            encyclopedia_index.add_child(instance=entry)
                            entry.save_revision().publish()
                            imported += 1
                            print(f"  ✅ Imported Encyclopedia: {title[:50]}...")
                    except Exception as e:
                        print(f"  ❌ Error: {e}")
                
                print(f"  Imported {imported} Encyclopedia entries in this batch")
                
            except Exception as e:
                print(f"  ❌ Error loading Encyclopedia: {e}")
    
    # Final check
    final_total = BlogPost.objects.count() + FAQArticle.objects.count() + EncyclopediaEntry.objects.count()
    progress = final_total / total_expected * 100
    
    print(f"\n🎯 Progress: {final_total}/{total_expected} ({progress:.1f}%)")
    
    if progress < 100:
        print("\n💡 Run this script again to import more content in batches")
    else:
        print("\n✅ 🎉 100% COMPLETE! All content successfully imported!")

if __name__ == "__main__":
    main()
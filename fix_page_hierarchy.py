#!/usr/bin/env python
"""Fix page hierarchy for newsletter and accessibility pages."""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ethicic.settings')
django.setup()

from wagtail.models import Site, Page
from public_site.models import HomePage
from public_site.models_newsletter import NewsletterPage, AccessibilityPage

# Get the home page
site = Site.objects.get(is_default_site=True)
home_page = site.root_page
print(f'Site root page: {home_page.title} (id: {home_page.id}, path: {home_page.url_path})')

# Check if pages need to be moved
newsletter = NewsletterPage.objects.first()
accessibility = AccessibilityPage.objects.first()

if newsletter:
    parent = newsletter.get_parent()
    print(f'\nNewsletter page parent: {parent.title} (id: {parent.id})')
    if parent.id != home_page.id:
        print(f'Moving newsletter page from {parent.title} to {home_page.title}')
        newsletter.move(home_page, pos='last-child')
        newsletter.save()
        newsletter.save_revision().publish()
        print(f'Newsletter page moved. New URL: {newsletter.url}')

if accessibility:
    parent = accessibility.get_parent()
    print(f'\nAccessibility page parent: {parent.title} (id: {parent.id})')
    if parent.id != home_page.id:
        print(f'Moving accessibility page from {parent.title} to {home_page.title}')
        accessibility.move(home_page, pos='last-child')
        accessibility.save()
        accessibility.save_revision().publish()
        print(f'Accessibility page moved. New URL: {accessibility.url}')

# Test the URLs
from django.test import Client
client = Client()
client.defaults['SERVER_NAME'] = 'ec1c.com'

print('\nTesting URLs:')
if newsletter:
    response = client.get(newsletter.url)
    print(f'Newsletter {newsletter.url}: {response.status_code}')
    
if accessibility:
    response = client.get(accessibility.url)
    print(f'Accessibility {accessibility.url}: {response.status_code}')
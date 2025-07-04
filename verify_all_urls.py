#!/usr/bin/env python
"""Verify all URLs are accessible."""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ethicic.settings')
django.setup()

# Add testserver to ALLOWED_HOSTS
from django.conf import settings
if 'testserver' not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS.append('testserver')

from django.test import Client
from django.urls import reverse

def test_all_urls():
    """Test all public URLs."""
    client = Client()
    
    # List of URLs to test with expected status codes
    urls_to_test = [
        # Main pages
        ('/', 200, 'Homepage'),
        ('/about/', 200, 'About page'),
        ('/process/', 200, 'Process page'),
        ('/faq/', 200, 'FAQ page'),
        ('/blog/', 200, 'Blog page'),
        ('/research/', 200, 'Research page'),
        ('/media/', 200, 'Media page'),
        ('/strategies/', 200, 'Strategies page'),
        ('/contact/', 200, 'Contact page'),
        ('/newsletter/', 200, 'Newsletter page'),
        ('/accessibility/', 200, 'Accessibility page'),
        ('/privacy-policy/', 200, 'Privacy policy'),
        ('/terms-of-service/', 200, 'Terms of service'),
        
        # Form endpoints
        ('/contact/submit/', 405, 'Contact form endpoint (GET not allowed)'),
        ('/newsletter/signup/', 405, 'Newsletter endpoint (GET not allowed)'),
        
        # HTMX endpoints
        ('/search/live/', 200, 'Live search endpoint'),
        
        # Static files
        ('/static/css/16-homepage.css', 200, 'Homepage CSS'),
        ('/static/css/garden-ui-theme.css', 200, 'Garden UI CSS'),
        ('/static/css/blog-unified.css', 200, 'Blog CSS'),
        ('/static/js/garden-core.js', 200, 'Garden Core JS'),
        ('/static/js/garden-panel.js', 200, 'Garden Panel JS'),
        ('/static/js/garden-theme-toggle.js', 200, 'Theme Toggle JS'),
        
        # Media files served directly by Django/WhiteNoise
        ('/media/', 404, 'Media root (no files)'),
        
        # API endpoints
        ('/api/contact/', 405, 'Contact API (GET not allowed)'),
        ('/api/newsletter/', 405, 'Newsletter API (GET not allowed)'),
    ]
    
    print("Testing all URLs...")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    for url, expected_status, name in urls_to_test:
        try:
            response = client.get(url, follow=False)
            status = response.status_code
            
            # Check if status matches expected or is a redirect (301/302)
            if status == expected_status or (expected_status == 200 and status in [301, 302]):
                print(f"✓ {name:<40} {url:<30} [{status}]")
                passed += 1
            else:
                print(f"✗ {name:<40} {url:<30} [{status}] (expected {expected_status})")
                failed += 1
                
        except Exception as e:
            print(f"✗ {name:<40} {url:<30} [ERROR: {str(e)[:30]}...]")
            failed += 1
    
    # Test POST endpoints
    print("\n" + "=" * 70)
    print("Testing POST endpoints...")
    
    post_tests = [
        ('/contact/submit/', {'name': 'Test', 'email': 'test@example.com', 'message': 'Test'}, 'Contact form POST'),
        ('/newsletter/signup/', {'email': 'test@example.com'}, 'Newsletter POST'),
    ]
    
    for url, data, name in post_tests:
        try:
            response = client.post(url, data=data)
            if response.status_code in [200, 302]:
                print(f"✓ {name:<40} {url:<30} [{response.status_code}]")
                passed += 1
            else:
                print(f"✗ {name:<40} {url:<30} [{response.status_code}]")
                failed += 1
        except Exception as e:
            print(f"✗ {name:<40} {url:<30} [ERROR: {str(e)[:30]}...]")
            failed += 1
    
    # Summary
    print("\n" + "=" * 70)
    print(f"Total tests: {passed + failed}")
    print(f"✓ Passed: {passed}")
    print(f"✗ Failed: {failed}")
    print(f"Success rate: {(passed / (passed + failed) * 100):.1f}%")
    
    return failed == 0

if __name__ == "__main__":
    success = test_all_urls()
    sys.exit(0 if success else 1)
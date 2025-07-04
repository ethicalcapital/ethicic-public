# Generated migration to update newsletter page content
from django.db import migrations


def update_newsletter_content(apps, schema_editor):
    """Update newsletter page content to be less committal."""
    NewsletterPage = apps.get_model('public_site', 'NewsletterPage')
    
    # Update the newsletter page content
    newsletter_pages = NewsletterPage.objects.all()
    for page in newsletter_pages:
        page.intro_text = '<p>Get our latest insights on ethical investing and portfolio management as they\'re published.</p>'
        page.benefits_title = 'Why Subscribe?'
        page.benefits_text = '''<ul>
                <li>Latest insights and ethical investing trends as they're published</li>
                <li>Research updates when available</li>
                <li>Early access to new features and investment opportunities</li>
                <li>Exclusive content not available on the website</li>
            </ul>'''
        page.privacy_text = '<p>We respect your privacy. Your email will only be used for our newsletter and you can unsubscribe at any time.</p>'
        page.save()


def reverse_newsletter_content(apps, schema_editor):
    """Reverse the newsletter page content changes."""
    NewsletterPage = apps.get_model('public_site', 'NewsletterPage')
    
    # Revert to original content
    newsletter_pages = NewsletterPage.objects.all()
    for page in newsletter_pages:
        page.intro_text = '<p>Stay updated with the latest insights on ethical investing and portfolio management.</p>'
        page.benefits_title = 'Why Subscribe?'
        page.benefits_text = '''<ul>
                <li>Monthly market insights and ethical investing trends</li>
                <li>Research updates and portfolio strategy discussions</li>
                <li>Early access to new features and investment opportunities</li>
                <li>Exclusive content not available on the website</li>
            </ul>'''
        page.privacy_text = '<p>We respect your privacy. Your email will only be used for our newsletter and you can unsubscribe at any time.</p>'
        page.save()


class Migration(migrations.Migration):

    dependencies = [
        ('public_site', '0015_remove_newsletter_accessibility_defaults'),
    ]

    operations = [
        migrations.RunPython(
            update_newsletter_content,
            reverse_newsletter_content
        ),
    ]
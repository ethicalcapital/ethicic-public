"""
Test fixtures for public site tests.

Creates minimal Wagtail page tree structure for testing.
"""

from django.contrib.auth.models import User
from wagtail.models import Page, Site


def create_test_page_tree():
    """Create minimal page tree for tests."""
    # Delete existing pages
    Page.objects.all().delete()

    # Create root page
    root = Page.get_first_root_node()
    if not root:
        root = Page.add_root(
            title="Root",
            slug="root",
        )

    # Create home page
    from public_site.models import HomePage

    home = HomePage(
        title="Test Home",
        slug="home",
        hero_title="Test Hero",
    )
    root.add_child(instance=home)

    # Create default site
    Site.objects.all().delete()
    Site.objects.create(
        hostname="localhost",
        port=80,
        root_page=home,
        is_default_site=True,
    )

    return root, home


def create_test_user(
    username="fixtureuser", email="test@example.com", password="testpass123"
):
    """Create a test user."""
    return User.objects.create_user(username=username, email=email, password=password)

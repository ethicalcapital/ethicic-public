"""Pytest configuration and fixtures."""

import pytest
from django.test import Client
from wagtail.models import Page, Site
from wagtail.models.i18n import Locale


@pytest.fixture
def client():
    """Return a Django test client."""
    return Client()


@pytest.fixture
def authenticated_client(client, django_user_model):
    """Return an authenticated test client."""
    user = django_user_model.objects.create_user(
        username="testuser",
        password="testpass123",  # nosec S106 - Test fixture only
        email="test@example.com",
    )
    client.force_login(user)
    return client


@pytest.fixture
def wagtail_site(db):
    """Create a Wagtail site for testing."""
    # Create default locale first
    locale, created = Locale.objects.get_or_create(
        language_code="en", defaults={"language_code": "en"}
    )

    # Get or create root page

    # Create root page if it doesn't exist
    root = Page.objects.filter(id=1).first()
    if not root:
        root = Page.add_root(title="Root", locale=locale)

    # Create a home page if it doesn't exist
    from public_site.models import HomePage

    home = HomePage.objects.filter(slug="home").first()
    if not home:
        home = HomePage(
            title="Test Home",
            slug="home",
            hero_title="Test Hero Title",
            hero_subtitle="<p>Test subtitle</p>",
            locale=locale,
        )
        root.add_child(instance=home)
        home.save_revision().publish()

    # Create or update site
    site = Site.objects.filter(is_default_site=True).first()
    if not site:
        site = Site.objects.create(
            hostname="testserver", root_page=home, is_default_site=True
        )
    else:
        site.root_page = home
        site.hostname = "testserver"
        site.save()

    return site


@pytest.fixture
def blog_index_page(wagtail_site):
    """Create a blog index page."""
    from wagtail.models.i18n import Locale

    from public_site.models import BlogIndexPage

    # Get default locale
    locale = Locale.objects.get(language_code="en")

    home = wagtail_site.root_page
    blog = BlogIndexPage.objects.filter(slug="blog").first()

    if not blog:
        blog = BlogIndexPage(
            title="Blog",
            slug="blog",
            intro_text="<p>Test blog intro</p>",
            locale=locale,
        )
        home.add_child(instance=blog)
        blog.save_revision().publish()

    return blog


@pytest.fixture
def sample_blog_post(blog_index_page):
    """Create a sample blog post."""
    from wagtail.models.i18n import Locale

    from public_site.models import BlogPost

    # Get default locale
    locale = Locale.objects.get(language_code="en")

    post = BlogPost(
        title="Test Blog Post",
        slug="test-blog-post",
        author="Test Author",
        excerpt="Test excerpt",
        body="<p>Test body content</p>",
        locale=locale,
    )
    blog_index_page.add_child(instance=post)
    post.save_revision().publish()

    return post


@pytest.fixture
def faq_index_page(wagtail_site):
    """Create an FAQ index page."""
    from wagtail.models.i18n import Locale

    from public_site.models import FAQIndexPage

    # Get default locale
    locale = Locale.objects.get(language_code="en")

    home = wagtail_site.root_page
    faq = FAQIndexPage.objects.filter(slug="faq").first()

    if not faq:
        faq = FAQIndexPage(
            title="FAQ",
            slug="faq",
            intro_text="<p>Frequently asked questions</p>",
            locale=locale,
        )
        home.add_child(instance=faq)
        faq.save_revision().publish()

    return faq


@pytest.fixture
def sample_faq_article(faq_index_page):
    """Create a sample FAQ article."""
    from wagtail.models.i18n import Locale

    from public_site.models import FAQArticle

    # Get default locale
    locale = Locale.objects.get(language_code="en")

    article = FAQArticle(
        title="What is the minimum investment?",
        slug="minimum-investment",
        summary="The minimum investment is $100,000",
        content="<p>Our minimum investment is $100,000.</p>",
        category="general",
        locale=locale,
    )
    faq_index_page.add_child(instance=article)
    article.save_revision().publish()

    return article


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """
    Automatically enable database access for all tests.
    This is required for Wagtail tests.
    """

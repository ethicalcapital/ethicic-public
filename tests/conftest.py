"""Pytest configuration and fixtures."""
import pytest
from django.test import Client
from wagtail.models import Page, Site
from wagtail.test.utils import WagtailPageTestCase


@pytest.fixture
def client():
    """Return a Django test client."""
    return Client()


@pytest.fixture
def authenticated_client(client, django_user_model):
    """Return an authenticated test client."""
    user = django_user_model.objects.create_user(
        username='testuser',
        password='testpass123',
        email='test@example.com'
    )
    client.force_login(user)
    return client


@pytest.fixture
def wagtail_site(db):
    """Create a Wagtail site for testing."""
    # Get or create root page
    root = Page.objects.get(id=1)
    
    # Create a home page if it doesn't exist
    from public_site.models import HomePage
    
    home = HomePage.objects.filter(slug='home').first()
    if not home:
        home = HomePage(
            title="Test Home",
            slug="home",
            hero_title="Test Hero Title",
            hero_subtitle="<p>Test subtitle</p>"
        )
        root.add_child(instance=home)
        home.save_revision().publish()
    
    # Create or update site
    site = Site.objects.filter(is_default_site=True).first()
    if not site:
        site = Site.objects.create(
            hostname='testserver',
            root_page=home,
            is_default_site=True
        )
    else:
        site.root_page = home
        site.hostname = 'testserver'
        site.save()
    
    return site


@pytest.fixture
def blog_index_page(wagtail_site):
    """Create a blog index page."""
    from public_site.models import BlogIndexPage
    
    home = wagtail_site.root_page
    blog = BlogIndexPage.objects.filter(slug='blog').first()
    
    if not blog:
        blog = BlogIndexPage(
            title="Blog",
            slug="blog",
            intro="<p>Test blog intro</p>"
        )
        home.add_child(instance=blog)
        blog.save_revision().publish()
    
    return blog


@pytest.fixture
def sample_blog_post(blog_index_page):
    """Create a sample blog post."""
    from public_site.models import BlogPost
    
    post = BlogPost(
        title="Test Blog Post",
        slug="test-blog-post",
        author="Test Author",
        excerpt="Test excerpt",
        body="<p>Test body content</p>"
    )
    blog_index_page.add_child(instance=post)
    post.save_revision().publish()
    
    return post


@pytest.fixture
def faq_index_page(wagtail_site):
    """Create an FAQ index page."""
    from public_site.models import FAQIndexPage
    
    home = wagtail_site.root_page
    faq = FAQIndexPage.objects.filter(slug='faq').first()
    
    if not faq:
        faq = FAQIndexPage(
            title="FAQ",
            slug="faq",
            intro="<p>Frequently asked questions</p>"
        )
        home.add_child(instance=faq)
        faq.save_revision().publish()
    
    return faq


@pytest.fixture
def sample_faq_article(faq_index_page):
    """Create a sample FAQ article."""
    from public_site.models import FAQArticle
    
    article = FAQArticle(
        title="What is the minimum investment?",
        slug="minimum-investment",
        summary="The minimum investment is $100,000",
        answer="<p>Our minimum investment is $100,000.</p>",
        category="general"
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
    pass
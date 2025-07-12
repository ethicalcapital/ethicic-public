"""
Tests for Wagtail page models in the public site.
"""

import os
import sys

# Import our Wagtail test base
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from datetime import timedelta

from django.utils import timezone

from public_site.models import (
    BlogPost,
    ContactPage,
    EncyclopediaEntry,
    EncyclopediaIndexPage,
    FAQIndexPage,
    HomePage,
    LegalPage,
    PRIDDQPage,
    StrategyListPage,
    StrategyPage,
    SupportTicket,
)
from public_site.tests.test_base import WagtailPublicSiteTestCase, WagtailTestCase


class HomePageTest(WagtailPublicSiteTestCase):
    """Test HomePage model."""

    def test_homepage_creation(self):
        """Test creating a home page."""
        if not self.home_page:
            self.skipTest("No home page available - Wagtail pages not set up")
        self.assertEqual(self.home_page.title, "Home")  # From WagtailTestCase setup
        self.assertEqual(self.home_page.slug, "home")
        self.assertEqual(self.home_page.hero_title, "Test Home Page")

    def test_homepage_fields(self):
        """Test all HomePage fields."""
        if not self.home_page:
            self.skipTest("No home page available - Wagtail pages not set up")
        # Update fields
        self.home_page.hero_tagline = "Test Tagline"
        self.home_page.hero_subtitle = "<p>Test subtitle</p>"
        self.home_page.excluded_percentage = "60%"
        self.home_page.since_year = "SINCE 2020"
        self.home_page.philosophy_title = "Test Philosophy"
        self.home_page.philosophy_content = "<p>Test philosophy content</p>"
        self.home_page.philosophy_highlight = "Test highlight"
        self.home_page.save()

        # Retrieve and verify
        page = HomePage.objects.get(id=self.home_page.id)
        self.assertEqual(page.hero_tagline, "Test Tagline")
        self.assertEqual(page.excluded_percentage, "60%")
        self.assertEqual(page.philosophy_title, "Test Philosophy")

    def test_homepage_template(self):
        """Test HomePage uses correct template."""
        if not self.home_page:
            self.skipTest("No home page available - Wagtail pages not set up")
        self.assertEqual(
            self.home_page.template, "public_site/homepage_accessible.html"
        )

    def test_homepage_verbose_names(self):
        """Test HomePage model meta options."""
        self.assertEqual(HomePage._meta.verbose_name, "Homepage")
        self.assertEqual(HomePage._meta.verbose_name_plural, "Homepages")


class BlogPostTest(WagtailPublicSiteTestCase):
    """Test BlogPost model."""

    def setUp(self):
        super().setUp()
        self.blog_index = self.create_test_blog_index()

    def test_blog_post_creation(self):
        """Test creating a blog post."""
        post = self.create_test_blog_post(parent=self.blog_index)
        self.assertEqual(post.title, "Test Blog Post")
        self.assertEqual(post.author, "Test Author")
        self.assertFalse(post.featured)

    def test_blog_post_featured(self):
        """Test featured blog posts."""
        featured_post = self.create_test_blog_post(
            parent=self.blog_index, title="Featured Post", featured=True
        )
        self.assertTrue(featured_post.featured)

    def test_blog_post_publish_date(self):
        """Test blog post publish dates."""
        past_date = timezone.now().date() - timedelta(days=30)
        old_post = self.create_test_blog_post(
            parent=self.blog_index, title="Old Post", publish_date=past_date
        )
        self.assertEqual(old_post.publish_date, past_date)

    def test_blog_post_tags(self):
        """Test blog post tagging."""
        post = self.create_test_blog_post(parent=self.blog_index)
        post.tags.add("investing", "ethics")
        post.save()

        # Check tags
        tags = list(post.tags.names())
        self.assertIn("investing", tags)
        self.assertIn("ethics", tags)

    def test_blog_post_content_field(self):
        """Test StreamField content on blog post."""
        from wagtail.rich_text import RichText

        post = self.create_test_blog_post(parent=self.blog_index)

        # Add StreamField content - RichTextBlock needs RichText object
        post.content = [
            ("rich_text", RichText("<p>Rich text content</p>")),
            (
                "key_statistic",
                {
                    "value": "57%",
                    "label": "S&P 500 Excluded",
                    "description": "Percentage of S&P 500 companies excluded by our criteria",
                    "significance_level": "high",
                },
            ),
        ]
        post.save()

        # Verify content
        self.assertEqual(len(post.content), 2)
        self.assertEqual(post.content[0].block_type, "rich_text")
        self.assertEqual(post.content[1].block_type, "key_statistic")

    def test_blog_post_search_fields(self):
        """Test blog post search field configuration."""
        search_fields = [field.field_name for field in BlogPost.search_fields]
        self.assertIn("excerpt", search_fields)
        self.assertIn("content", search_fields)
        self.assertIn("body", search_fields)


class BlogIndexPageTest(WagtailPublicSiteTestCase):
    """Test BlogIndexPage model."""

    def setUp(self):
        super().setUp()
        self.blog_index = self.create_test_blog_index()

    def test_blog_index_creation(self):
        """Test creating a blog index page."""
        self.assertEqual(self.blog_index.title, "Blog")
        self.assertEqual(self.blog_index.slug, "blog")

    def test_get_posts(self):
        """Test retrieving blog posts."""
        # Create some posts
        post1 = self.create_test_blog_post(self.blog_index, "Post 1")
        post2 = self.create_test_blog_post(self.blog_index, "Post 2")
        post3 = self.create_test_blog_post(self.blog_index, "Draft Post")
        post3.unpublish()

        # Get posts
        posts = self.blog_index.get_posts()
        self.assertEqual(posts.count(), 2)  # Only published posts

    def test_get_featured_posts(self):
        """Test retrieving featured posts."""
        # Create regular and featured posts
        regular = self.create_test_blog_post(self.blog_index, "Regular")
        featured1 = self.create_test_blog_post(
            self.blog_index, "Featured 1", featured=True
        )
        featured2 = self.create_test_blog_post(
            self.blog_index, "Featured 2", featured=True
        )

        featured_posts = self.blog_index.get_featured_posts()
        self.assertIn(featured1, featured_posts)
        self.assertIn(featured2, featured_posts)
        self.assertNotIn(regular, featured_posts)

    def test_get_posts_by_tag(self):
        """Test filtering posts by tag."""
        post1 = self.create_test_blog_post(self.blog_index, "Tagged Post")
        post1.tags.add("investing")
        post1.save()

        post2 = self.create_test_blog_post(self.blog_index, "Other Post")
        post2.tags.add("ethics")
        post2.save()

        investing_posts = self.blog_index.get_posts_by_tag("investing")
        self.assertEqual(investing_posts.count(), 1)
        self.assertIn(post1, investing_posts)

    def test_routable_paths(self):
        """Test BlogIndexPage routable paths."""
        # Test that the page responds to different paths
        response = self.client.get(self.blog_index.url)
        self.assertEqual(response.status_code, 200)

        # Test tag route
        post = self.create_test_blog_post(self.blog_index)
        post.tags.add("test-tag")
        post.save()

        response = self.client.get(f"{self.blog_index.url}tag/test-tag/")
        self.assertEqual(response.status_code, 200)


class StrategyPageTest(WagtailPublicSiteTestCase):
    """Test StrategyPage model."""

    def test_strategy_page_creation(self):
        """Test creating a strategy page."""
        strategy = self.create_test_strategy_page(
            title="Growth Strategy", strategy_label="Our Flagship"
        )

        self.assertEqual(strategy.title, "Growth Strategy")
        self.assertEqual(strategy.strategy_label, "Our Flagship")
        self.assertEqual(strategy.risk_level, "Full market exposure")

    def test_strategy_page_performance_data(self):
        """Test strategy performance data fields."""
        strategy = self.create_test_strategy_page()

        # Update performance data
        strategy.ytd_return = "12.5%"
        strategy.one_year_return = "18.3%"
        strategy.three_year_return = "10.2%"
        strategy.since_inception_return = "14.7%"
        strategy.inception_date = timezone.now().date() - timedelta(days=1000)
        strategy.save()

        # Verify
        saved = StrategyPage.objects.get(id=strategy.id)
        self.assertEqual(saved.ytd_return, "12.5%")
        self.assertEqual(saved.one_year_return, "18.3%")


class StrategyListPageTest(WagtailPublicSiteTestCase):
    """Test StrategyListPage model."""

    def test_strategy_list_page_creation(self):
        """Test creating a strategy list page."""
        list_page = StrategyListPage(
            title="Strategies",
            slug="strategies",
        )
        if not self.home_page:
            self.skipTest("No home page available - Wagtail pages not set up")
        self.home_page.add_child(instance=list_page)

        self.assertEqual(list_page.title, "Strategies")

    def test_get_strategies(self):
        """Test retrieving strategies with flagship first."""
        list_page = StrategyListPage(
            title="Strategies",
            slug="strategies",
        )
        if not self.home_page:
            self.skipTest("No home page available - Wagtail pages not set up")
        self.home_page.add_child(instance=list_page)

        # Create strategies
        flagship = self.create_test_strategy_page(
            parent=list_page, title="Flagship Growth", strategy_label="Our Flagship"
        )

        regular = self.create_test_strategy_page(
            parent=list_page, title="Income Strategy", strategy_label="Income Focus"
        )

        strategies = list_page.get_strategies()

        # Flagship should be first
        self.assertEqual(strategies[0], flagship)
        self.assertEqual(strategies[1], regular)


class FAQArticleTest(WagtailPublicSiteTestCase):
    """Test FAQArticle model."""

    def test_faq_article_creation(self):
        """Test creating an FAQ article."""
        article = self.create_test_faq_article(
            title="How do I get started?", category="account"
        )

        self.assertEqual(article.title, "How do I get started?")
        self.assertEqual(article.category, "account")
        self.assertEqual(article.priority, 1)

    def test_faq_article_related(self):
        """Test FAQ article related articles."""
        faq_index = FAQIndexPage(title="FAQ", slug="faq")
        if not self.home_page:
            self.skipTest("No home page available - Wagtail pages not set up")
        self.home_page.add_child(instance=faq_index)

        article1 = self.create_test_faq_article(parent=faq_index, title="Article 1")
        article2 = self.create_test_faq_article(parent=faq_index, title="Article 2")

        # Set related articles
        article1.related_articles = "Article 2"
        article1.save()

        related = article1.get_related_articles_list()
        self.assertIn(article2, related)
        self.assertNotIn(article1, related)  # Should exclude self


class MediaPageTest(WagtailPublicSiteTestCase):
    """Test MediaPage and MediaItem models."""

    def test_media_page_creation(self):
        """Test creating a media page with items."""
        media_page = self.create_test_media_page()

        self.assertEqual(media_page.title, "Media")
        self.assertEqual(media_page.media_items.count(), 5)

    def test_media_item_ordering(self):
        """Test media items are ordered correctly."""
        media_page = self.create_test_media_page()
        items = media_page.media_items.all()

        # Check featured item is first
        self.assertTrue(items[0].featured)

        # Check dates are in descending order
        for i in range(len(items) - 1):
            self.assertGreaterEqual(
                items[i].publication_date, items[i + 1].publication_date
            )

    def test_media_item_fields(self):
        """Test MediaItem model fields."""
        media_page = self.create_test_media_page()
        item = media_page.media_items.first()

        self.assertIsNotNone(item.title)
        self.assertIsNotNone(item.description)
        self.assertIsNotNone(item.publication)
        self.assertIsNotNone(item.publication_date)
        self.assertIsNotNone(item.external_url)


class ContactPageTest(WagtailPublicSiteTestCase):
    """Test ContactPage model."""

    def test_contact_page_creation(self):
        """Test creating a contact page."""
        contact_page = ContactPage(
            title="Contact",
            slug="contact",
            show_contact_form=True,
            email="hello@ethicic.com",
        )
        if not self.home_page:
            self.skipTest("No home page available - Wagtail pages not set up")
        self.home_page.add_child(instance=contact_page)

        self.assertEqual(contact_page.title, "Contact")
        self.assertTrue(contact_page.show_contact_form)
        self.assertEqual(contact_page.email, "hello@ethicic.com")

    def test_contact_page_routable(self):
        """Test ContactPage is routable."""
        contact_page = ContactPage(
            title="Contact",
            slug="contact",
        )
        if not self.home_page:
            self.skipTest("No home page available - Wagtail pages not set up")
        self.home_page.add_child(instance=contact_page)

        response = self.client.get(contact_page.url)
        self.assertEqual(response.status_code, 200)


class SupportTicketTest(WagtailTestCase):
    """Test SupportTicket model."""

    def test_support_ticket_creation(self):
        """Test creating a support ticket."""
        ticket = SupportTicket.objects.create(
            name="John Doe",
            email="john.doe@example.com",
            subject="Test Subject",
            message="Test message content",
            status="new",
        )

        self.assertEqual(ticket.name, "John Doe")
        self.assertEqual(ticket.status, "new")
        self.assertEqual(
            str(ticket), f"#{ticket.id} - Test Subject - john.doe@example.com"
        )

    def test_support_ticket_ordering(self):
        """Test support tickets are ordered by creation date."""
        # Create tickets with different timestamps
        old_ticket = SupportTicket.objects.create(
            name="Old Ticket",
            email="old@example.com",
            subject="Old",
            message="Old message",
        )

        # Wait a moment
        import time

        time.sleep(0.1)

        new_ticket = SupportTicket.objects.create(
            name="New Ticket",
            email="new@example.com",
            subject="New",
            message="New message",
        )

        tickets = list(SupportTicket.objects.all())
        self.assertEqual(tickets[0], new_ticket)  # Newest first
        self.assertEqual(tickets[1], old_ticket)


class PRIDDQPageTest(WagtailPublicSiteTestCase):
    """Test PRIDDQPage model."""

    def test_pri_ddq_page_creation(self):
        """Test creating a PRI DDQ page."""
        ddq_page = PRIDDQPage(
            title="PRI DDQ",
            slug="pri-ddq",
            hero_title="PRI Due Diligence Questionnaire",
            hero_subtitle="Our comprehensive ESG approach",
            screening_policy_url="https://example.com/screening-policy",
            executive_summary="<p>Test summary</p>",
        )
        if not self.home_page:
            self.skipTest("No home page available - Wagtail pages not set up")
        self.home_page.add_child(instance=ddq_page)

        self.assertEqual(ddq_page.title, "PRI DDQ")
        self.assertIn("Test summary", ddq_page.executive_summary)

    def test_pri_ddq_updated_at(self):
        """Test PRIDDQPage auto-updates updated_at field."""
        ddq_page = PRIDDQPage(
            title="PRI DDQ",
            slug="pri-ddq",
            hero_title="PRI Due Diligence Questionnaire",
            hero_subtitle="Our comprehensive ESG approach",
            screening_policy_url="https://example.com/screening-policy",
        )
        if not self.home_page:
            self.skipTest("No home page available - Wagtail pages not set up")
        self.home_page.add_child(instance=ddq_page)

        # Save should update the updated_at field
        ddq_page.save()

        # Check format is "Month Year"
        import re

        pattern = r"^[A-Z][a-z]+ \d{4}$"  # e.g., "January 2025"
        self.assertIsNotNone(re.match(pattern, ddq_page.updated_at))

    def test_get_ddq_questions_for_faq(self):
        """Test extracting DDQ questions for FAQ."""
        ddq_page = PRIDDQPage(
            title="PRI DDQ",
            slug="pri-ddq",
            hero_title="PRI Due Diligence Questionnaire",
            hero_subtitle="Our comprehensive ESG approach",
            screening_policy_url="https://example.com/screening-policy",
        )
        if not self.home_page:
            self.skipTest("No home page available - Wagtail pages not set up")
        self.home_page.add_child(instance=ddq_page)

        questions = ddq_page.get_ddq_questions_for_faq()

        # Should have questions
        self.assertGreater(len(questions), 0)

        # Check question structure
        for q in questions:
            self.assertIn("question", q)
            self.assertIn("answer", q)
            self.assertIn("category", q)


class EncyclopediaEntryTest(WagtailPublicSiteTestCase):
    """Test EncyclopediaEntry model."""

    def test_encyclopedia_entry_creation(self):
        """Test creating an encyclopedia entry."""
        index = EncyclopediaIndexPage(title="Encyclopedia", slug="encyclopedia")
        if not self.home_page:
            self.skipTest("No home page available - Wagtail pages not set up")
        self.home_page.add_child(instance=index)

        entry = EncyclopediaEntry(
            title="Asset Allocation",
            slug="asset-allocation",
            summary="The process of dividing investments among different asset categories",
            detailed_content="<p>Detailed explanation of asset allocation...</p>",
            category="strategy",
            difficulty_level="beginner",
        )
        index.add_child(instance=entry)

        self.assertEqual(entry.title, "Asset Allocation")
        self.assertEqual(entry.category, "strategy")
        self.assertEqual(entry.difficulty_level, "beginner")

    def test_encyclopedia_get_related_entries(self):
        """Test getting related encyclopedia entries."""
        index = EncyclopediaIndexPage(title="Encyclopedia", slug="encyclopedia")
        if not self.home_page:
            self.skipTest("No home page available - Wagtail pages not set up")
        self.home_page.add_child(instance=index)

        entry1 = EncyclopediaEntry(
            title="Diversification",
            slug="diversification",
            summary="Test summary",
            detailed_content="<p>Content</p>",
            related_terms="risk, allocation",
        )
        index.add_child(instance=entry1)

        entry2 = EncyclopediaEntry(
            title="Risk Management",
            slug="risk-management",
            summary="Test summary",
            detailed_content="<p>Content</p>",
        )
        index.add_child(instance=entry2)

        related = entry1.get_related_entries()
        self.assertIn(entry2, related)


class LegalPageTest(WagtailPublicSiteTestCase):
    """Test LegalPage model."""

    def test_legal_page_creation(self):
        """Test creating a legal page."""
        legal_page = LegalPage(
            title="Privacy Policy",
            slug="privacy-policy",
            content="<p>Privacy policy content...</p>",
            effective_date=timezone.now().date(),
        )
        if not self.home_page:
            self.skipTest("No home page available - Wagtail pages not set up")
        self.home_page.add_child(instance=legal_page)

        self.assertEqual(legal_page.title, "Privacy Policy")
        self.assertIsNotNone(legal_page.effective_date)
        self.assertIsNotNone(legal_page.updated_at)

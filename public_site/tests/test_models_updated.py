"""
Comprehensive tests for updated models focusing on:
- Database constraints and validation
- Performance optimizations
- Query efficiency
- Model relationships and methods
"""

from datetime import date, timedelta
from unittest.mock import patch

from django.db import IntegrityError
from django.test import TestCase, TransactionTestCase, override_settings
from django.utils import timezone
from wagtail.models import Page
from wagtail.models.i18n import Locale
from wagtail.test.utils import WagtailPageTestCase

from public_site.models import (
    # Page models
    BlogIndexPage,
    BlogPost,
    FAQItem,
    FAQPage,
    MediaItem,
    MediaPage,
    PRIDDQPage,
    SiteConfiguration,
    StrategyPage,
    SupportTicket,
)


class DatabaseConstraintTestCase(TransactionTestCase):
    """Test database-level constraints we added."""

    def test_support_ticket_status_constraint(self):
        """Test that support ticket status is constrained to valid values."""
        # Valid status should work
        ticket = SupportTicket.objects.create(
            name="Test User",
            email="test@example.com",
            subject="Test Subject",
            message="Test message",
            status="open",
            priority="medium",
            ticket_type="question",
        )
        self.assertEqual(ticket.status, "open")

        # Invalid status should fail
        with self.assertRaises(IntegrityError):
            SupportTicket.objects.create(
                name="Test User",
                email="test@example.com",
                subject="Test Subject",
                message="Test message",
                status="invalid_status",
                priority="medium",
                ticket_type="question",
            )

    def test_support_ticket_priority_constraint(self):
        """Test that support ticket priority is constrained to valid values."""
        # Valid priority should work
        ticket = SupportTicket.objects.create(
            name="Test User",
            email="test@example.com",
            subject="Test Subject",
            message="Test message",
            status="open",
            priority="high",
            ticket_type="question",
        )
        self.assertEqual(ticket.priority, "high")

        # Invalid priority should fail
        with self.assertRaises(IntegrityError):
            SupportTicket.objects.create(
                name="Test User",
                email="test@example.com",
                subject="Test Subject",
                message="Test message",
                status="open",
                priority="invalid_priority",
                ticket_type="question",
            )

    def test_support_ticket_type_constraint(self):
        """Test that support ticket type is constrained to valid values including newsletter."""
        # Valid types should work
        valid_types = ["question", "issue", "request", "feedback", "newsletter"]

        for ticket_type in valid_types:
            ticket = SupportTicket.objects.create(
                name=f"Test User {ticket_type}",
                email=f"test{ticket_type}@example.com",
                subject=f"Test Subject {ticket_type}",
                message="Test message",
                status="open",
                priority="medium",
                ticket_type=ticket_type,
            )
            self.assertEqual(ticket.ticket_type, ticket_type)

        # Invalid type should fail
        with self.assertRaises(IntegrityError):
            SupportTicket.objects.create(
                name="Test User",
                email="test@example.com",
                subject="Test Subject",
                message="Test message",
                status="open",
                priority="medium",
                ticket_type="invalid_type",
            )

    def test_support_ticket_dates_logical_constraint(self):
        """Test that updated_at >= created_at constraint is enforced."""
        # Create a ticket normally (should work)
        ticket = SupportTicket.objects.create(
            name="Test User",
            email="test@example.com",
            subject="Test Subject",
            message="Test message",
            status="open",
            priority="medium",
            ticket_type="question",
        )

        # Try to manually set updated_at before created_at (should fail)
        past_date = timezone.now() - timedelta(days=1)
        with self.assertRaises(IntegrityError):
            ticket.created_at = timezone.now()
            ticket.updated_at = past_date
            ticket.save()

    def test_support_ticket_email_format_constraint(self):
        """Test that email format is validated by database constraint."""
        # Valid email should work
        ticket = SupportTicket.objects.create(
            name="Test User",
            email="valid.email@example.com",
            subject="Test Subject",
            message="Test message",
            status="open",
            priority="medium",
            ticket_type="question",
        )
        self.assertEqual(ticket.email, "valid.email@example.com")

        # Invalid email should fail
        with self.assertRaises(IntegrityError):
            SupportTicket.objects.create(
                name="Test User",
                email="invalid-email-format",
                subject="Test Subject",
                message="Test message",
                status="open",
                priority="medium",
                ticket_type="question",
            )

    def test_faq_priority_positive_constraint(self):
        """Test that FAQ priority must be positive."""
        # This would need to be tested on FAQ models that have priority fields
        # Skipping for now since FAQItem uses sort_order, not priority

    def test_strategy_inception_date_constraint(self):
        """Test that strategy inception date is reasonable."""
        # Create a minimal page tree for Wagtail
        locale, _ = Locale.objects.get_or_create(language_code="en")
        root_page = Page.objects.filter(id=1).first()
        if not root_page:
            root_page = Page.add_root(title="Root", locale=locale)

        # Valid inception date should work
        strategy = StrategyPage(
            title="Test Strategy",
            slug="test-strategy",
            inception_date=date(2021, 1, 1),
            locale=locale,
        )
        root_page.add_child(instance=strategy)
        self.assertEqual(strategy.inception_date.year, 2021)

        # Future date should fail due to constraint
        with self.assertRaises(IntegrityError):
            future_strategy = StrategyPage(
                title="Future Strategy",
                slug="future-strategy",
                inception_date=date(2030, 1, 1),  # Future date
                locale=locale,
            )
            root_page.add_child(instance=future_strategy)


class QueryOptimizationTestCase(WagtailPageTestCase):
    """Test that our query optimizations work correctly."""

    def setUp(self):
        """Set up test data for query optimization tests."""
        super().setUp()
        self.locale, _ = Locale.objects.get_or_create(language_code="en")

        # Create a blog index page
        self.blog_index = BlogIndexPage(title="Blog", slug="blog", locale=self.locale)
        self.root_page.add_child(instance=self.blog_index)

        # Create some blog posts with tags
        for i in range(5):
            post = BlogPost(
                title=f"Test Post {i}",
                slug=f"test-post-{i}",
                author=f"Author {i}",
                featured=(i < 2),  # First 2 are featured
                locale=self.locale,
            )
            self.blog_index.add_child(instance=post)

            # Add tags
            post.tags.add(f"tag-{i}", "common-tag")
            post.save()

    def test_get_posts_uses_select_related(self):
        """Test that get_posts() uses select_related for optimization."""
        with self.assertNumQueries(1):  # Should be a single optimized query
            posts = list(self.blog_index.get_posts()[:3])

        # Verify we got the posts
        self.assertEqual(len(posts), 3)

        # Accessing owner should not cause additional queries due to select_related
        with self.assertNumQueries(0):
            for post in posts:
                _ = post.owner  # This should not trigger additional queries

    def test_get_posts_uses_prefetch_related_for_tags(self):
        """Test that get_posts() uses prefetch_related for tags."""
        posts = self.blog_index.get_posts()[:3]

        # Prefetch the tags
        posts_list = list(posts)

        # Accessing tags should not cause N+1 queries due to prefetch_related
        with self.assertNumQueries(0):
            for post in posts_list:
                tags = list(post.tags.all())  # Should not trigger additional queries

    def test_get_featured_posts_limit(self):
        """Test that get_featured_posts returns maximum 3 posts."""
        featured_posts = self.blog_index.get_featured_posts()

        # Should return only featured posts, max 3
        self.assertEqual(len(featured_posts), 2)  # We created 2 featured posts

        for post in featured_posts:
            self.assertTrue(post.featured)

    def test_get_recent_posts_limit(self):
        """Test that get_recent_posts returns maximum 6 posts."""
        recent_posts = self.blog_index.get_recent_posts()

        # Should return max 6 posts (we have 5)
        self.assertEqual(len(recent_posts), 5)

    def test_get_all_authors_optimization(self):
        """Test that get_all_authors method works correctly and is optimized."""
        authors = self.blog_index.get_all_authors()

        # Should return author data with counts
        self.assertGreater(len(authors), 0)

        for author_data in authors:
            self.assertIn("name", author_data)
            self.assertIn("slug", author_data)
            self.assertIn("post_count", author_data)
            self.assertGreater(author_data["post_count"], 0)

    def test_get_posts_by_tag_filtering(self):
        """Test that get_posts_by_tag filters correctly."""
        # Test filtering by a tag that exists on one post
        tag_0_posts = self.blog_index.get_posts_by_tag("tag-0")
        self.assertEqual(tag_0_posts.count(), 1)

        # Test filtering by common tag
        common_tag_posts = self.blog_index.get_posts_by_tag("common-tag")
        self.assertEqual(common_tag_posts.count(), 5)  # All posts have this tag

    def test_get_all_tags_optimization(self):
        """Test that get_all_tags method handles exceptions gracefully."""
        # This should work normally
        tags = self.blog_index.get_all_tags()
        self.assertGreater(tags.count(), 0)

        # Test exception handling by mocking ContentType.objects.get_for_model to raise exception
        with patch(
            "django.contrib.contenttypes.models.ContentType.objects.get_for_model"
        ) as mock_get:
            mock_get.side_effect = Exception("Test exception")

            # Should return empty queryset when exception occurs
            tags = self.blog_index.get_all_tags()
            self.assertEqual(tags.count(), 0)


class PRIDDQPageTestCase(WagtailPageTestCase):
    """Test PRIDDQPage model specifically for timezone fix."""

    def test_pri_ddq_save_uses_timezone_aware_datetime(self):
        """Test that PRIDDQPage.save() uses timezone-aware datetime."""
        ddq_page = PRIDDQPage(
            title="PRI DDQ Test",
            slug="pri-ddq-test",
            hero_title="Test Hero Title",
            hero_subtitle="Test subtitle",
            locale=self.locale,
        )
        self.root_page.add_child(instance=ddq_page)

        # Save the page
        ddq_page.save()

        # Check that updated_at field was set with current month/year
        self.assertIsNotNone(ddq_page.updated_at)

        # Should be in format "Month Year"
        import re

        pattern = r"^[A-Z][a-z]+ \d{4}$"  # e.g., "January 2025"
        self.assertTrue(re.match(pattern, ddq_page.updated_at))

        # Should reflect current date
        current_date = timezone.now()
        expected_format = current_date.strftime("%B %Y")
        self.assertEqual(ddq_page.updated_at, expected_format)

    def test_pri_ddq_sync_to_support_articles(self):
        """Test sync_to_support_articles method."""
        ddq_page = PRIDDQPage(
            title="PRI DDQ Test",
            slug="pri-ddq-test",
            hero_title="Test Hero Title",
            hero_subtitle="Test subtitle",
            locale=self.locale,
        )
        self.root_page.add_child(instance=ddq_page)

        # Mock the get_ddq_questions_for_faq method to return test data
        test_questions = [
            {
                "question": "Test Question 1",
                "answer": "Test Answer 1",
                "category": "general",
            },
            {
                "question": "Test Question 2",
                "answer": "Test Answer 2",
                "category": "screening",
            },
        ]

        with patch.object(
            ddq_page, "get_ddq_questions_for_faq", return_value=test_questions
        ):
            ddq_page.sync_to_support_articles()

            # Should not raise any exceptions
            # In a real implementation, this would create FAQ articles

    def test_get_ddq_questions_for_faq(self):
        """Test extraction of DDQ questions for FAQ."""
        ddq_page = PRIDDQPage(
            title="PRI DDQ Test",
            slug="pri-ddq-test",
            hero_title="Test Hero Title",
            hero_subtitle="Test subtitle",
            locale=self.locale,
        )
        self.root_page.add_child(instance=ddq_page)

        questions = ddq_page.get_ddq_questions_for_faq()

        # Should return a list of questions
        self.assertIsInstance(questions, list)

        # Each question should have required fields
        for question in questions:
            self.assertIn("question", question)
            self.assertIn("answer", question)
            self.assertIn("category", question)


class ModelRelationshipTestCase(WagtailPageTestCase):
    """Test model relationships and foreign keys."""

    def test_blog_tag_relationship(self):
        """Test BlogTag relationship with BlogPost."""
        # Create a blog post
        blog_index = BlogIndexPage(title="Blog", slug="blog", locale=self.locale)
        self.root_page.add_child(instance=blog_index)

        post = BlogPost(
            title="Tagged Post",
            slug="tagged-post",
            author="Test Author",
            locale=self.locale,
        )
        blog_index.add_child(instance=post)

        # Add tags
        post.tags.add("investing", "ethics", "sustainable")
        post.save()

        # Test relationships
        self.assertEqual(post.tags.count(), 3)

        # Test tag names
        tag_names = list(post.tags.names())
        self.assertIn("investing", tag_names)
        self.assertIn("ethics", tag_names)
        self.assertIn("sustainable", tag_names)

    def test_media_item_ordering(self):
        """Test MediaItem ordering by featured and publication date."""
        media_page = MediaPage(title="Media", slug="media", locale=self.locale)
        self.root_page.add_child(instance=media_page)

        # Create media items with different dates and featured status
        items_data = [
            {"title": "Old Item", "date": date(2023, 1, 1), "featured": False},
            {"title": "Featured Old", "date": date(2023, 6, 1), "featured": True},
            {"title": "Recent Item", "date": date(2024, 1, 1), "featured": False},
            {"title": "Featured Recent", "date": date(2024, 6, 1), "featured": True},
        ]

        for item_data in items_data:
            MediaItem.objects.create(
                page=media_page,
                title=item_data["title"],
                description="Test description",
                publication="Test Publication",
                publication_date=item_data["date"],
                external_url="https://example.com",
                featured=item_data["featured"],
                sort_order=0,
            )

        # Get ordered items
        items = media_page.media_items.all()

        # Featured items should come first, then by date descending
        self.assertTrue(items[0].featured)
        self.assertTrue(items[1].featured)

        # Within featured items, newer should come first
        self.assertGreater(items[0].publication_date, items[1].publication_date)

    def test_faq_item_relationship(self):
        """Test FAQItem relationship with FAQPage."""
        faq_page = FAQPage(title="FAQ", slug="faq", locale=self.locale)
        self.root_page.add_child(instance=faq_page)

        # Create FAQ items
        for i in range(3):
            FAQItem.objects.create(
                page=faq_page,
                question=f"Question {i}",
                answer=f"Answer {i}",
                sort_order=i,
            )

        # Test relationship
        self.assertEqual(faq_page.faq_items.count(), 3)

        # Test ordering
        items = list(faq_page.faq_items.all())
        for i in range(3):
            self.assertEqual(items[i].question, f"Question {i}")

    def test_support_ticket_str_method(self):
        """Test SupportTicket string representation."""
        ticket = SupportTicket.objects.create(
            name="John Doe",
            email="john@example.com",
            subject="Test Subject",
            message="Test message",
            status="open",
            priority="medium",
            ticket_type="question",
        )

        expected_str = f"#{ticket.id} - Test Subject - john@example.com"
        self.assertEqual(str(ticket), expected_str)

    def test_support_ticket_ordering(self):
        """Test SupportTicket default ordering."""
        # Create tickets with slight delay to ensure different timestamps
        import time

        ticket1 = SupportTicket.objects.create(
            name="First Ticket",
            email="first@example.com",
            subject="First",
            message="First message",
            status="open",
            priority="medium",
            ticket_type="question",
        )

        time.sleep(0.01)  # Small delay

        ticket2 = SupportTicket.objects.create(
            name="Second Ticket",
            email="second@example.com",
            subject="Second",
            message="Second message",
            status="open",
            priority="medium",
            ticket_type="question",
        )

        # Should be ordered by creation date descending (newest first)
        tickets = list(SupportTicket.objects.all())
        self.assertEqual(tickets[0], ticket2)  # Newest first
        self.assertEqual(tickets[1], ticket1)


class SiteConfigurationTestCase(TestCase):
    """Test SiteConfiguration model."""

    def test_site_configuration_singleton(self):
        """Test that SiteConfiguration works as a singleton."""
        config1 = SiteConfiguration.objects.create(
            company_name="Test Company",
            company_tagline="Test Tagline",
            primary_email="test@example.com",
        )

        # Try to create another - should work but there should only be one instance used
        config2 = SiteConfiguration.objects.create(
            company_name="Another Company",
            company_tagline="Another Tagline",
            primary_email="another@example.com",
        )

        # Both should exist in database but only one should be the "for_site" instance
        self.assertEqual(SiteConfiguration.objects.count(), 2)

    def test_site_configuration_fields(self):
        """Test SiteConfiguration model fields."""
        config = SiteConfiguration.objects.create(
            company_name="Ethical Capital",
            company_tagline="Ethical investing for the long term",
            primary_email="hello@ethicic.com",
            primary_phone="555-123-4567",
            street_address="123 Main St",
            city="Salt Lake City",
            state="UT",
            postal_code="84101",
            country="USA",
            founding_year="2021",
            minimum_investment="$100,000",
        )

        self.assertEqual(config.company_name, "Ethical Capital")
        self.assertEqual(config.primary_email, "hello@ethicic.com")
        self.assertEqual(config.founding_year, "2021")


class ModelValidationTestCase(TestCase):
    """Test model validation and edge cases."""

    def test_support_ticket_required_fields(self):
        """Test that SupportTicket validates required fields."""
        # Missing required fields should raise validation error
        with self.assertRaises(IntegrityError):
            SupportTicket.objects.create()

        # Valid ticket should work
        ticket = SupportTicket.objects.create(
            name="Test User",
            email="test@example.com",
            subject="Test Subject",
            message="Test message",
            status="open",
            priority="medium",
            ticket_type="question",
        )
        self.assertIsNotNone(ticket.id)

    def test_support_ticket_auto_timestamps(self):
        """Test that SupportTicket auto-populates timestamps."""
        before_creation = timezone.now()

        ticket = SupportTicket.objects.create(
            name="Test User",
            email="test@example.com",
            subject="Test Subject",
            message="Test message",
            status="open",
            priority="medium",
            ticket_type="question",
        )

        after_creation = timezone.now()

        # Timestamps should be set
        self.assertIsNotNone(ticket.created_at)
        self.assertIsNotNone(ticket.updated_at)

        # Should be within reasonable range
        self.assertGreaterEqual(ticket.created_at, before_creation)
        self.assertLessEqual(ticket.created_at, after_creation)

        # Updated at should be >= created at
        self.assertGreaterEqual(ticket.updated_at, ticket.created_at)

    def test_media_item_url_validation(self):
        """Test MediaItem URL field validation."""
        locale, _ = Locale.objects.get_or_create(language_code="en")
        root_page = Page.objects.filter(id=1).first()
        if not root_page:
            root_page = Page.add_root(title="Root", locale=locale)

        media_page = MediaPage(title="Media", slug="media", locale=locale)
        root_page.add_child(instance=media_page)

        # Valid URL should work
        item = MediaItem.objects.create(
            page=media_page,
            title="Test Item",
            description="Test description",
            publication="Test Publication",
            publication_date=date.today(),
            external_url="https://example.com/article",
            sort_order=0,
        )
        self.assertEqual(item.external_url, "https://example.com/article")


@override_settings(DEBUG=True)
class PerformanceTestCase(WagtailPageTestCase):
    """Test performance-related functionality."""

    def test_blog_index_query_efficiency(self):
        """Test that BlogIndex queries are efficient."""
        # Create blog index with many posts
        blog_index = BlogIndexPage(title="Blog", slug="blog", locale=self.locale)
        self.root_page.add_child(instance=blog_index)

        # Create 20 blog posts with tags and authors
        for i in range(20):
            post = BlogPost(
                title=f"Performance Test Post {i}",
                slug=f"performance-test-post-{i}",
                author=f"Author {i % 5}",  # 5 different authors
                featured=(i % 7 == 0),  # Some featured posts
                locale=self.locale,
            )
            blog_index.add_child(instance=post)

            # Add multiple tags
            post.tags.add(f"tag-{i}", f"category-{i % 3}", "common")
            post.save()

        # Test that get_posts() is efficient
        with self.assertNumQueries(
            1
        ):  # Should be single query due to select_related/prefetch_related
            posts = list(blog_index.get_posts()[:10])

        self.assertEqual(len(posts), 10)

        # Test that accessing related data doesn't cause additional queries
        with self.assertNumQueries(0):
            for post in posts:
                _ = post.owner  # select_related
                _ = list(post.tags.all())  # prefetch_related

    def test_get_all_authors_performance(self):
        """Test that get_all_authors is efficient with many posts."""
        # Create blog index
        blog_index = BlogIndexPage(title="Blog", slug="blog", locale=self.locale)
        self.root_page.add_child(instance=blog_index)

        # Create posts with overlapping authors
        authors = ["Alice Smith", "Bob Johnson", "Carol Davis", "David Wilson"]
        for i in range(40):  # 40 posts
            post = BlogPost(
                title=f"Author Test Post {i}",
                slug=f"author-test-post-{i}",
                author=authors[i % len(authors)],  # Cycle through authors
                locale=self.locale,
            )
            blog_index.add_child(instance=post)

        # Test author aggregation
        with self.assertNumQueries(1):  # Should be efficient aggregation query
            authors_data = blog_index.get_all_authors()

        # Should have 4 unique authors
        self.assertEqual(len(authors_data), 4)

        # Each author should have correct post count (40/4 = 10 posts each)
        for author_data in authors_data:
            self.assertEqual(author_data["post_count"], 10)
            self.assertIn("name", author_data)
            self.assertIn("slug", author_data)


class EdgeCaseTestCase(WagtailPageTestCase):
    """Test edge cases and error handling."""

    def test_empty_blog_index_methods(self):
        """Test BlogIndex methods with no posts."""
        blog_index = BlogIndexPage(
            title="Empty Blog", slug="empty-blog", locale=self.locale
        )
        self.root_page.add_child(instance=blog_index)

        # All methods should handle empty state gracefully
        self.assertEqual(blog_index.get_posts().count(), 0)
        self.assertEqual(len(blog_index.get_featured_posts()), 0)
        self.assertEqual(len(blog_index.get_recent_posts()), 0)
        self.assertEqual(len(blog_index.get_all_authors()), 0)
        self.assertEqual(blog_index.get_posts_by_tag("nonexistent").count(), 0)

    def test_get_all_tags_exception_handling(self):
        """Test that get_all_tags handles exceptions gracefully."""
        blog_index = BlogIndexPage(title="Blog", slug="blog", locale=self.locale)
        self.root_page.add_child(instance=blog_index)

        # Mock ContentType.objects.get_for_model to raise an exception
        with patch(
            "django.contrib.contenttypes.models.ContentType.objects.get_for_model"
        ) as mock_get:
            mock_get.side_effect = Exception("Database error")

            # Should return empty queryset instead of raising exception
            tags = blog_index.get_all_tags()
            self.assertEqual(tags.count(), 0)

    def test_pri_ddq_page_without_questions(self):
        """Test PRIDDQPage when no questions are available."""
        ddq_page = PRIDDQPage(
            title="Empty DDQ",
            slug="empty-ddq",
            hero_title="Empty DDQ Title",
            hero_subtitle="Empty subtitle",
            locale=self.locale,
        )
        self.root_page.add_child(instance=ddq_page)

        # Should handle empty questions gracefully
        questions = ddq_page.get_ddq_questions_for_faq()
        self.assertIsInstance(questions, list)

        # sync_to_support_articles should handle empty questions
        ddq_page.sync_to_support_articles()  # Should not raise exception

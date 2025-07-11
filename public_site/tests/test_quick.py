"""
Quick test to verify test infrastructure is working.
"""

from django.test import TestCase

from public_site.models import SupportTicket


class QuickSmokeTest(TestCase):
    """Quick smoke test to verify tests can run."""

    def test_basic_import(self):
        """Test we can import models."""
        self.assertTrue(True)

    def test_create_support_ticket(self):
        """Test we can create a support ticket."""
        ticket = SupportTicket.objects.create(
            name="Test User",
            email="test@example.com",
            subject="Test Subject",
            message="Test message",
            status="new",
        )

        self.assertEqual(ticket.name, "Test User")
        self.assertEqual(ticket.status, "new")
        self.assertEqual(SupportTicket.objects.count(), 1)

    def test_url_access(self):
        """Test we can access a basic URL."""
        # Test a simple API endpoint that doesn't require Wagtail pages
        response = self.client.get("/api/status/")
        self.assertEqual(response.status_code, 200)

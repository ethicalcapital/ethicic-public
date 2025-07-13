"""Standalone email utilities for public site deployment.

Extracted from core.email_utils to eliminate dependencies.
"""

import logging

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

logger = logging.getLogger(__name__)


def send_contact_notification(contact_data):
    """
    Send email notification for contact form submissions.

    Args:
        contact_data (dict): Contact form data

    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        subject = f"New Contact Form Submission - {contact_data.get('name', 'Unknown')}"

        # Send to configured contact email
        recipient_email = getattr(settings, "CONTACT_EMAIL", "hello@ethicic.com")

        message = f"""
New contact form submission:

Name: {contact_data.get("name", "Not provided")}
Email: {contact_data.get("email", "Not provided")}
Subject: {contact_data.get("subject", "Not provided")}
Message: {contact_data.get("message", "Not provided")}

Submitted: {timezone.now()}
Source: {contact_data.get("source", "Website")}
"""

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient_email],
            fail_silently=False,
        )

        logger.info(
            f"Contact notification sent for {contact_data.get('email', 'unknown')}"
        )
        return True

    except Exception as e:
        logger.error(f"Failed to send contact notification: {e}")
        return False


def send_newsletter_notification(email, source="website"):
    """
    Send notification for newsletter subscriptions.

    Args:
        email (str): Subscriber email
        source (str): Source of subscription

    Returns:
        bool: True if email sent successfully, False otherwise
    """
    # Validate email input
    if not email or not email.strip():
        logger.warning("Newsletter notification called with empty email")
        return False

    # Basic email format validation
    if "@" not in email or "." not in email.split("@")[-1]:
        logger.warning(
            f"Newsletter notification called with invalid email format: {email}"
        )
        return False

    try:
        subject = f"New Newsletter Subscription - {email}"

        # Send to configured contact email
        recipient_email = getattr(settings, "CONTACT_EMAIL", "hello@ethicic.com")

        message = f"""
New newsletter subscription:

Email: {email}
Source: {source}
Subscribed: {timezone.now()}
"""

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient_email],
            fail_silently=False,
        )

        logger.info(f"Newsletter notification sent for {email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send newsletter notification: {e}")
        return False


def send_compliance_email(subject, message, recipient_email):
    """
    Send compliance-related emails.

    Args:
        subject (str): Email subject
        message (str): Email message
        recipient_email (str): Recipient email address

    Returns:
        bool: True if email sent successfully, False otherwise
    """
    # Validate inputs - allow empty strings but not None
    if subject is None or message is None or not recipient_email:
        logger.warning("Compliance email called with missing parameters")
        return False

    if not recipient_email.strip():
        logger.warning("Compliance email called with empty recipient")
        return False

    # Basic email format validation
    if "@" not in recipient_email or "." not in recipient_email.split("@")[-1]:
        logger.warning(
            f"Compliance email called with invalid email format: {recipient_email}"
        )
        return False

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient_email],
            fail_silently=False,
        )

        logger.info(f"Compliance email sent to {recipient_email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send compliance email: {e}")
        return False

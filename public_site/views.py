"""Public Site Views - Minimal version without CRM dependencies
Provides basic form handling and API endpoints for Wagtail-based public site
"""

import json
import logging

from django.conf import settings

# Import requests for mocking purposes in tests
try:
    import requests
except ImportError:
    requests = None
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from wagtail.models import Page

# Try to import Query, fallback if not available
try:
    from wagtail.contrib.search_promotions.models import Query
except ImportError:
    try:
        # Fallback to old location for backward compatibility
        from wagtail.search.models import Query
    except ImportError:
        Query = None

from .forms import (
    AccessibleContactForm,
    AccessibleNewsletterForm,
    OnboardingForm,
)
from .models import MediaItem, SupportTicket

logger = logging.getLogger(__name__)


# Error handlers
def custom_404(request, exception):
    """Custom 404 error page"""
    return render(request, "404.html", status=404)


def custom_500(request):
    """Custom 500 error page with fallback"""
    try:
        return render(request, "500.html", status=500)
    except Exception as e:
        # Fallback if template rendering fails
        import logging

        from django.http import HttpResponse

        logger = logging.getLogger(__name__)
        logger.error(f"Error handler failed to render template: {e}")

        html = """
        <!DOCTYPE html>
        <html>
        <head><title>Server Error</title></head>
        <body>
            <h1>500 - Server Error</h1>
            <p>An error occurred while processing your request.</p>
        </body>
        </html>
        """
        return HttpResponse(html, status=500, content_type="text/html")


# Standalone constants already imported above


# Try to import CRM models for database operations
try:
    from crm.models import Contact
    from crm.models.interactions import ContactInteraction

    CRM_AVAILABLE = True
    logger.info("CRM integration available - using direct database access")
except ImportError:
    # CRM models not available (public site running independently)
    Contact = None
    ContactInteraction = None
    CRM_AVAILABLE = False
    logger.info("CRM integration not available - using fallback handling")

# Try to import AI services
try:
    from ai_services.providers import get_provider  # noqa: F401

    AI_SERVICES_AVAILABLE = True
    logger.info("AI services available")
except ImportError:
    AI_SERVICES_AVAILABLE = False
    logger.info("AI services not available - features will be disabled")


def send_fallback_email(contact_data):
    """Send email when API is unavailable"""
    if hasattr(settings, "CONTACT_EMAIL") and settings.CONTACT_EMAIL:
        try:
            from .standalone_email_utils import send_compliance_email

            message = f"""
New contact form submission from public website:

Name: {contact_data["name"]}
Email: {contact_data["email"]}
Company: {contact_data.get("company", "Not provided")}
Subject: {contact_data["subject"]}

Message:
{contact_data["message"]}

NOTE: This was submitted via email fallback because the main platform API was unavailable.
            """

            send_compliance_email(
                subject=f"New Contact Form: {contact_data['subject']}",
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.CONTACT_EMAIL],
                fail_silently=True,
            )
        except Exception:
            logger.exception("Failed to send fallback contact form email")


@require_http_methods(["POST"])
def contact_form_submit(request):
    """Handle contact form submissions from public site via API calls"""
    form = AccessibleContactForm(request.POST, request=request)

    if form.is_valid():
        contact_data = form.cleaned_data

        try:
            # Create SupportTicket directly for simplicity and reliability
            from public_site.models import SupportTicket

            # Split name into first and last name
            name_parts = contact_data["name"].split() if contact_data["name"] else [""]
            first_name = name_parts[0] if name_parts else ""
            last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

            # Create support ticket
            ticket = SupportTicket.objects.create(
                name=contact_data["name"],
                email=contact_data["email"],
                company=contact_data.get("company", ""),
                subject=f"{contact_data['subject']} - {contact_data.get('company', 'Individual')}",
                message=contact_data["message"],
                ticket_type="question",
                status="open",
            )

            logger.info(
                "Contact form submitted successfully, created ticket #%s", ticket.id
            )

            # Try secure API submission first, fallback to local storage
            secure_submission_result = None
            try:
                from public_site.services.platform_client import platform_client

                submission_data = {
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": contact_data["email"],
                    "subject": ticket.subject,
                    "message": contact_data["message"],
                    "category": contact_data["subject"],
                    "company": contact_data.get("company", ""),
                    "source": "public_website",
                    "ticket_id": ticket.id,
                }

                secure_submission_result = platform_client.secure_contact_submission(
                    submission_data
                )

                if secure_submission_result:
                    # Store submission ID for tracking
                    ticket.external_reference = secure_submission_result.get(
                        "submission_id"
                    )
                    ticket.save()
                    logger.info(
                        "Contact submitted via secure API: %s",
                        secure_submission_result.get("submission_id"),
                    )
                else:
                    logger.info("Secure API not available, using local storage only")

            except Exception as e:
                logger.warning("Secure API submission failed: %s", e)
                # Fallback email as backup notification method
                send_fallback_email(contact_data)

            messages.success(
                request,
                "Thank you for your message! We will get back to you within 24 hours.",
            )

            # Redirect back to contact page with success
            return redirect("/contact/")

        except Exception:
            logger.exception("Error processing contact form")
            messages.error(
                request,
                "There was an error processing your request. Please try again or email us directly.",
            )
            return redirect("/contact/")

    else:
        # Form has errors - redirect back with error message
        error_messages = [
            f"{field}: {error}"
            for field, errors in form.errors.items()
            for error in errors
        ]

        logger.error("Contact form validation errors: %s", form.errors)
        messages.error(
            request,
            f"Please correct the following errors: {', '.join(error_messages)}",
        )
        return redirect("/contact/")


@require_http_methods(["POST"])
def newsletter_signup(request):
    """Handle newsletter signup submissions"""
    form = AccessibleNewsletterForm(request.POST)

    # Check if this is an HTMX request
    is_htmx = request.headers.get("HX-Request") == "true"

    if form.is_valid():
        email = form.cleaned_data["email"]

        try:
            # Log the signup
            logger.info("Newsletter signup: %s", email)

            # Try to create/update CRM Contact for newsletter subscriber
            try:
                from crm.models import Contact
                from crm.models.choices import ContactStatus, ContactType

                # Check if contact already exists
                contact, created = Contact.objects.get_or_create(
                    email=email,
                    defaults={
                        "full_name": "Newsletter Subscriber",
                        "first_name": "Newsletter",
                        "last_name": "Subscriber",
                        "contact_type": ContactType.INDIVIDUAL,
                        "status": ContactStatus.COLD_LEAD,
                        "opt_in_marketing": True,
                        "source": "Newsletter Page Signup",
                        "notes": "Subscribed via newsletter page",
                        "preferences": {
                            "newsletter_subscribed": True,
                            "newsletter_subscribed_date": timezone.now().isoformat(),
                            "newsletter_source": "newsletter_page",
                        },
                    },
                )

                if not created:
                    # Update existing contact to subscribe to newsletter
                    contact.opt_in_marketing = True
                    newsletter_prefs = contact.preferences.get(
                        "newsletter_subscribed", False
                    )
                    if not newsletter_prefs:
                        contact.preferences.update(
                            {
                                "newsletter_subscribed": True,
                                "newsletter_subscribed_date": timezone.now().isoformat(),
                                "newsletter_source": "newsletter_page",
                            }
                        )
                        contact.notes = (
                            (contact.notes or "")
                            + f"\nRe-subscribed to newsletter on {timezone.now().date()}"
                        )
                        contact.save()

                logger.info(
                    f"{'Created' if created else 'Updated'} CRM contact for newsletter subscriber: {email}"
                )

            except ImportError:
                # Fallback to SupportTicket if CRM models not available
                logger.warning(
                    "CRM models not available, falling back to SupportTicket"
                )
                SupportTicket.objects.create(
                    name="Newsletter Subscriber",
                    email=email,
                    subject="Newsletter Signup",
                    message="Newsletter subscription request",
                    ticket_type="newsletter",
                    status="resolved",
                )

            # Handle HTMX response
            if is_htmx:
                return render(
                    request,
                    "public_site/partials/newsletter_success.html",
                    {"email": email},
                )

            messages.success(
                request,
                "Thank you for subscribing! You will receive our newsletter updates.",
            )

        except Exception:
            logger.exception("Error processing newsletter signup")

            if is_htmx:
                return render(
                    request,
                    "public_site/partials/newsletter_error.html",
                    {
                        "error": "There was an error with your subscription. Please try again."
                    },
                )

            messages.error(
                request,
                "There was an error with your subscription. Please try again.",
            )

    else:
        if is_htmx:
            return render(
                request,
                "public_site/newsletter_page.html",
                {"form": form, "errors": form.errors},
            )

        messages.error(request, "Please provide a valid email address.")

    # Redirect back to the page they came from
    return redirect(request.META.get("HTTP_REFERER", "/"))


def classify_contact_priority(form_type, form_data):
    """Classify contact priority and status based on engagement AND business criteria."""
    # Import here to avoid dependency issues
    try:
        from crm.models.choices import ContactStatus, PriorityLevel
    except ImportError:
        # Fallback for when CRM is not available
        class ContactStatus:
            COLD_LEAD = "COLD_LEAD"
            WARM_LEAD = "WARM_LEAD"
            PROSPECT = "PROSPECT"

        class PriorityLevel:
            LOW = 1
            MEDIUM = 2
            HIGH = 3
            CRITICAL = 4

    importance_score = 0.5  # Default
    priority_level = PriorityLevel.MEDIUM
    contact_status = ContactStatus.COLD_LEAD  # Default to cold lead

    return contact_status, priority_level, importance_score


def create_or_update_contact(email, form_data, form_type, user=None):
    """Create or update CRM contact with business-focused deduplication and classification."""
    # Import here to avoid dependency issues
    try:
        from crm.models import Contact
        from crm.models.choices import (  # noqa: F401
            ContactStatus,
            ContactType,
            PriorityLevel,
        )

        # Get contact classification
        contact_status, priority_level, importance_score = classify_contact_priority(
            form_type, form_data
        )

        # Try to find existing contact
        contact = Contact.objects.filter(email=email).first()
        created = False

        if contact:
            # Update existing contact with new information
            if form_data.get("name") and not contact.full_name:
                contact.full_name = form_data["name"]
            contact.last_interaction = timezone.now()
            contact.interaction_count += 1
            contact.save()
        else:
            # Create new contact
            created = True
            full_name = (
                form_data.get("name")
                or f"{form_data.get('first_name', '')} {form_data.get('last_name', '')}".strip()
            )

            contact = Contact.objects.create(
                email=email,
                full_name=full_name,
                first_name=form_data.get("first_name", ""),
                last_name=form_data.get("last_name", ""),
                company=form_data.get("company", ""),
                job_title=form_data.get("role", ""),
                phone_primary=form_data.get("phone", ""),
                status=contact_status,
                priority_level=priority_level,
                importance_score=importance_score,
                last_interaction=timezone.now(),
                interaction_count=1,
                source=f"website_{form_type}",
                created_by=user,
            )

        return contact, created
    except ImportError:
        # When CRM is not available, return a mock object
        class MockContact:
            def __init__(self):
                self.id = 1
                self.email = email
                self.full_name = form_data.get("name", "")
                self.contact_status = "COLD_LEAD"

        return MockContact(), True


def _build_full_name(first, middle, last):
    """Build full name from components."""
    name_parts = [first or ""]
    if middle:
        name_parts.append(middle)
    name_parts.append(last or "")
    return " ".join(filter(None, name_parts))


def _build_full_address(form_data):
    """Build full address from form data."""
    address_parts = [form_data.get("street_address", "")]
    if form_data.get("street_address_2"):
        address_parts.append(form_data.get("street_address_2"))
    address_parts.extend(
        [
            form_data.get("city", ""),
            form_data.get("state", ""),
            form_data.get("zip_code", ""),
            form_data.get("country", ""),
        ]
    )
    return ", ".join(filter(None, address_parts))


def _format_currency(value):
    """Format numeric string as currency."""
    if value and value.isdigit():
        return f"${int(value):,}"
    return value


def _build_basic_info_parts(form_data, full_name, full_address):
    """Build basic information message parts."""
    return [
        "## Onboarding Application\n",
        f"**Name:** {full_name}",
        f"**Email:** {form_data.get('email', '')}",
        f"**Phone:** {form_data.get('phone', '')}",
        f"**Mailing Address:** {full_address}",
        f"**Pronouns:** {form_data.get('pronouns', '')}",
        f"**Birthday:** {form_data.get('birthday', '')}",
        f"**Employment Status:** {form_data.get('employment_status', '')}",
        f"**Marital Status:** {form_data.get('marital_status', '')}",
    ]


def _add_co_client_info(message_parts, form_data):
    """Add co-client information to message parts if applicable."""
    if form_data.get("add_co_client") == "yes":
        co_full_name = _build_full_name(
            form_data.get("co_client_first_name"),
            form_data.get("co_client_middle_names"),
            form_data.get("co_client_last_name"),
        )

        message_parts.extend(
            [
                "\n## Co-Client Information",
                f"**Name:** {co_full_name}",
                f"**Email:** {form_data.get('co_client_email', '')}",
                f"**Phone:** {form_data.get('co_client_phone', '')}",
                f"**Pronouns:** {form_data.get('co_client_pronouns', '')}",
                f"**Birthday:** {form_data.get('co_client_birthday', '')}",
                f"**Employment Status:** {form_data.get('co_client_employment_status', '')}",
                f"**Employer:** {form_data.get('co_client_employer_name', '')}",
                f"**Share Address:** {form_data.get('co_client_share_address', '')}",
            ]
        )


def _add_financial_context(message_parts, form_data):
    """Add financial context to message parts."""
    message_parts.extend(
        [
            "\n## Financial Context",
            f"**Investment Experience:** {form_data.get('investment_experience', '')}",
            f"**Net Worth:** {_format_currency(form_data.get('net_worth', ''))}",
            f"**Liquid Net Worth:** {_format_currency(form_data.get('liquid_net_worth', ''))}",
            f"**Investable Net Worth:** {_format_currency(form_data.get('investable_net_worth', ''))}",
        ]
    )

    if form_data.get("initial_investment"):
        formatted_investment = _format_currency(form_data.get("initial_investment", ""))
        message_parts.append(f"**Initial Investment:** {formatted_investment}")


def _add_ethical_considerations(message_parts, form_data):
    """Add ethical considerations to message parts."""
    fields = [
        ("ethical_considerations", "Ethical Considerations"),
        ("ethical_considerations_other", "Other Ethical Considerations"),
        ("divestment_movements", "Divestment Movements"),
        ("divestment_movements_other", "Other Divestment Movements"),
        ("understanding_importance_other", "Understanding Importance (Other)"),
        ("ethical_evolution_other", "Ethical Evolution (Other)"),
        ("ethical_concerns_unrecognized", "Unrecognized Ethical Concerns"),
        ("financial_team_coordinate", "Financial Team Coordination"),
        ("professional_referrals", "Professional Referrals"),
        ("professional_referrals_other", "Other Professional Referrals"),
        ("anything_else", "Additional Information"),
    ]

    for field_name, label in fields:
        value = form_data.get(field_name)
        if value:
            if isinstance(value, list):
                value = ", ".join(value)
            message_parts.append(f"\n**{label}:** {value}")


def _handle_secure_submission(
    ticket, form_data, full_name, full_address, comprehensive_message
):
    """Handle secure API submission with fallback."""
    try:
        from public_site.services.platform_client import platform_client

        onboarding_data = {
            "name": full_name,
            "email": form_data.get("email"),
            "phone": form_data.get("phone"),
            "address": full_address,
            "birthday": form_data.get("birthday"),
            "pronouns": form_data.get("pronouns"),
            "employment_status": form_data.get("employment_status"),
            "marital_status": form_data.get("marital_status"),
            "communication_preferences": form_data.get("communication_preference", []),
            "net_worth": form_data.get("net_worth"),
            "liquid_net_worth": form_data.get("liquid_net_worth"),
            "investable_net_worth": form_data.get("investable_net_worth"),
            "investment_experience": form_data.get("investment_experience"),
            "comprehensive_message": comprehensive_message,
            "ticket_id": ticket.id,
            "source": "onboarding_form",
        }

        if form_data.get("add_co_client") == "yes":
            co_full_name = _build_full_name(
                form_data.get("co_client_first_name"),
                form_data.get("co_client_middle_names"),
                form_data.get("co_client_last_name"),
            )

            onboarding_data["co_client"] = {
                "name": co_full_name,
                "email": form_data.get("co_client_email"),
                "phone": form_data.get("co_client_phone"),
                "pronouns": form_data.get("co_client_pronouns"),
                "birthday": form_data.get("co_client_birthday"),
                "employment_status": form_data.get("co_client_employment_status"),
            }

        result = platform_client.secure_onboarding_submission(onboarding_data)

        if result:
            ticket.external_reference = result.get("submission_id")
            ticket.save()
            logger.info(
                "Onboarding submitted via secure API: %s", result.get("submission_id")
            )
            return result
        logger.info("Secure API not available, using local storage only")

    except Exception as e:
        logger.warning("Secure API submission failed: %s", e)
        from public_site.standalone_email_utils import send_fallback_email

        send_fallback_email(
            {
                "name": full_name,
                "email": form_data.get("email"),
                "subject": "Onboarding Application",
                "message": comprehensive_message,
            }
        )

    return None


@require_http_methods(["POST"])
def onboarding_form_submit(request):
    """Handle comprehensive onboarding form submissions"""
    form = OnboardingForm(request.POST, request=request)
    is_htmx = request.headers.get("HX-Request") == "true"

    if form.is_valid():
        form_data = form.cleaned_data

        try:
            # Build names and addresses
            full_name = _build_full_name(
                form_data.get("first_name"),
                form_data.get("middle_names"),
                form_data.get("last_name"),
            )
            full_address = _build_full_address(form_data)

            # Build message parts
            message_parts = _build_basic_info_parts(form_data, full_name, full_address)

            # Add communication preferences
            if form_data.get("communication_preference"):
                message_parts.append(
                    f"\n**Communication Preferences:** {', '.join(form_data.get('communication_preference', []))}"
                )

            # Add co-client info
            _add_co_client_info(message_parts, form_data)

            # Add financial context
            _add_financial_context(message_parts, form_data)

            # Add ethical considerations
            _add_ethical_considerations(message_parts, form_data)

            # Create support ticket
            ticket = SupportTicket.objects.create(
                name=full_name,
                email=form_data["email"],
                subject=f"Onboarding Application - {full_name}",
                message="\n".join(message_parts),
                ticket_type="onboarding",
                status="open",
            )

            logger.info(
                "Onboarding form submitted successfully, created ticket #%s", ticket.id
            )

            # Handle secure submission
            comprehensive_message = "\n".join(message_parts)
            _handle_secure_submission(
                ticket, form_data, full_name, full_address, comprehensive_message
            )

            # Handle HTMX request
            if is_htmx:
                return render(
                    request,
                    "public_site/partials/onboarding_success.html",
                    {
                        "message": "Thank you for your application!",
                        "details": "We have received your information and will review it shortly.",
                        "ticket_id": ticket.id if ticket else None,
                    },
                )

            messages.success(
                request,
                "Thank you for your application! We have received your information and will review it shortly.",
            )

            return redirect("/onboarding/thank-you/")

        except Exception:
            logger.exception("Error processing onboarding form")

            if is_htmx:
                return render(
                    request,
                    "public_site/partials/onboarding_error.html",
                    {
                        "message": "There was an error processing your application.",
                        "details": "Please try again or contact us directly.",
                    },
                )

            messages.error(
                request,
                "There was an error processing your application. Please try again or contact us directly.",
            )
            return redirect("/onboarding/")

    else:
        # Form has errors
        # Check if this is spam (honeypot field filled)
        if request.POST.get("honeypot"):
            # Even for HTMX requests, redirect for spam detection
            return redirect("/onboarding/")

        if is_htmx:
            return render(
                request,
                "public_site/partials/onboarding_error.html",
                {
                    "message": "Please correct the following errors:",
                    "errors": form.errors,
                },
            )

        error_messages = [
            f"{field}: {error}"
            for field, errors in form.errors.items()
            for error in errors
        ]

        messages.error(
            request,
            f"Please correct the following errors: {', '.join(error_messages)}",
        )
        return redirect("/onboarding/")


def onboarding_thank_you(request):
    """Thank you page after onboarding application submission"""
    context = {
        "page_title": "Application Received",
        "heading": "Thank You for Your Application!",
        "message": "We have received your onboarding application and will review it shortly.",
        "next_steps": [
            "Account review and approval (1-2 business days)",
            "Schedule a consultation with your adviser",
            "Fund your account and begin investing",
            "Access your personalized investment dashboard",
        ],
    }

    return render(request, "public_site/onboarding_thank_you.html", context)


def contact_success(request):
    """Contact form success page"""
    context = {
        "page_title": "Message Sent",
        "heading": "Thank You for Contacting Us!",
        "message": "We have received your message and will respond within 24 hours.",
    }
    return render(request, "public_site/contact_success.html", context)


@api_view(["POST"])
@permission_classes([AllowAny])
def contact_api(request):
    """API endpoint for contact form submissions - supports both JSON and HTMX"""
    try:
        # Check if this is an HTMX request
        is_htmx = request.headers.get("HX-Request") == "true"

        # Use DRF request.data which handles both JSON and form data
        # This will also handle JSON parsing errors automatically
        try:
            data = request.data
        except Exception as parse_error:
            logger.warning("JSON parse error in contact API: %s", parse_error)
            if is_htmx:
                return render(
                    request,
                    "public_site/partials/form_error.html",
                    {
                        "message": "Invalid form data. Please check your input and try again."
                    },
                )
            return Response(
                {
                    "success": False,
                    "message": "Invalid JSON format in request.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create a mock request object for the form with necessary attributes
        class MockRequest:
            def __init__(self):
                self.META = {}

        mock_request = MockRequest()

        # For API endpoints, add required spam protection fields if missing
        if "human_check" not in data:
            # Add a simple default value for API usage
            data = data.copy() if hasattr(data, "copy") else dict(data)
            data["human_check"] = "2"  # Simple default for API

        form = AccessibleContactForm(data, request=mock_request)
        # For API usage, set a simple math answer to bypass validation
        form.math_answer = 2

        if form.is_valid():
            contact_data = form.cleaned_data

            # Create support ticket
            ticket = SupportTicket.objects.create(
                name=contact_data["name"],
                email=contact_data["email"],
                company=contact_data.get("company", ""),
                subject=f"{contact_data['subject']} - {contact_data.get('company', 'Individual')}",
                message=contact_data["message"],
                ticket_type="question",
                status="open",
            )

            # Send notification email (if configured)
            if hasattr(settings, "CONTACT_EMAIL") and settings.CONTACT_EMAIL:
                try:
                    from .standalone_email_utils import send_compliance_email

                    message = f"""
New contact form submission:

Name: {contact_data["name"]}
Email: {contact_data["email"]}
Company: {contact_data.get("company", "Not provided")}
Subject: {contact_data["subject"]}

Message:
{contact_data["message"]}

Support Ticket ID: {ticket.id}
                    """

                    send_compliance_email(
                        subject=f"New Contact Form: {contact_data['subject']}",
                        message=message,
                        recipient_email=settings.CONTACT_EMAIL,
                    )
                except Exception:
                    logger.exception("Failed to send contact form email")

            # Return appropriate response based on request type
            if is_htmx:
                return render(
                    request,
                    "public_site/partials/form_success.html",
                    {
                        "message": "Thank you for your message! We will get back to you within 24 hours.",
                        "ticket_id": ticket.id,
                    },
                )

            return Response(
                {
                    "success": True,
                    "message": "Thank you for your message! We will get back to you within 24 hours.",
                    "ticket_id": ticket.id,
                },
                status=status.HTTP_201_CREATED,
            )

        # Form has errors
        if is_htmx:
            return render(
                request,
                "public_site/partials/form_error.html",
                {
                    "message": "Please correct the form errors.",
                    "errors": form.errors,
                },
            )

        return Response(
            {
                "success": False,
                "message": "Please correct the form errors.",
                "errors": form.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    except Exception:
        logger.exception("Error in contact API")
        if is_htmx:
            return render(
                request,
                "public_site/partials/form_error.html",
                {
                    "message": "There was an error processing your request. Please try again.",
                },
            )

        return Response(
            {
                "success": False,
                "message": "There was an error processing your request. Please try again.",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def newsletter_api(request):
    """API endpoint for newsletter signup - supports both JSON and HTMX"""
    try:
        # Check if this is an HTMX request
        is_htmx = request.headers.get("HX-Request") == "true"

        # Use DRF request.data which handles both JSON and form data
        data = request.data

        form = AccessibleNewsletterForm(data)

        if form.is_valid():
            email = form.cleaned_data["email"]

            # Create a simple support ticket to track newsletter signups
            SupportTicket.objects.create(
                name="Newsletter Subscriber",
                email=email,
                subject="Newsletter Signup",
                message="Newsletter subscription request via API",
                ticket_type="newsletter",
                status="resolved",
            )

            logger.info("Newsletter signup via API: %s", email)

            if is_htmx:
                return render(
                    request,
                    "public_site/partials/newsletter_success.html",
                    {
                        "email": email,
                    },
                )

            return Response(
                {
                    "success": True,
                    "message": "Thank you for subscribing! You will receive our newsletter updates.",
                },
                status=status.HTTP_201_CREATED,
            )

        if is_htmx:
            return render(
                request,
                "public_site/partials/newsletter_error.html",
                {
                    "errors": form.errors,
                },
            )

        return Response(
            {
                "success": False,
                "message": "Please provide a valid email address.",
                "errors": form.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    except Exception:
        logger.exception("Error in newsletter API")
        if is_htmx:
            return render(
                request,
                "public_site/partials/newsletter_error.html",
                {
                    "message": "There was an error with your subscription. Please try again.",
                },
            )

        return Response(
            {
                "success": False,
                "message": "There was an error with your subscription. Please try again.",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([AllowAny])
def site_status_api(request):
    """API endpoint for site status and health check"""
    try:
        from django.db import connection

        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")

        # Get basic site statistics
        stats = {
            "status": "healthy",
            "timestamp": timezone.now().isoformat(),
            "database": "connected",
            "support_tickets": {
                "total": SupportTicket.objects.count(),
                "open": SupportTicket.objects.filter(status="open").count(),
                "resolved": SupportTicket.objects.filter(status="resolved").count(),
            },
        }

        return Response(stats, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception("Site status check failed")
        return Response(
            {
                "status": "unhealthy",
                "timestamp": timezone.now().isoformat(),
                "error": str(e),
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


@api_view(["GET"])
@permission_classes([AllowAny])
def get_site_navigation(request):
    """API endpoint to get site navigation structure"""
    from wagtail.models import Page

    try:
        # Get the site root page
        root_page = Page.objects.filter(depth=2).first()

        if root_page:
            # Get main navigation pages (depth 3)
            nav_pages = Page.objects.child_of(root_page).live().public().in_menu()

            navigation = [
                {
                    "title": page.title,
                    "url": page.url,
                    "slug": page.slug,
                }
                for page in nav_pages
            ]

            # Only return the navigation if we have items, otherwise fall back
            if navigation:
                return Response(
                    {"navigation": navigation},
                    status=status.HTTP_200_OK,
                )

    except Exception:
        logger.exception("Error getting site navigation")

    # Fallback navigation structure - updated to use /blog/ instead of /research/
    fallback_navigation = [
        {"title": "Home", "url": "/", "slug": "home"},
        {"title": "About", "url": "/about/", "slug": "about"},
        {"title": "Blog", "url": "/blog/", "slug": "blog"},
        {"title": "Process", "url": "/process/", "slug": "process"},
        {"title": "Pricing", "url": "/pricing/", "slug": "pricing"},
        {"title": "Support", "url": "/support/", "slug": "support"},
        {"title": "Contact", "url": "/contact/", "slug": "contact"},
    ]

    return Response(
        {"navigation": fallback_navigation},
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def get_footer_links(request):
    """API endpoint to get footer link structure"""
    footer_links = {
        "company": [
            {"title": "About Us", "url": "/about/"},
            {"title": "Our Process", "url": "/process/"},
            {"title": "Blog", "url": "/blog/"},  # Updated from research to blog
            {"title": "Media", "url": "/media/"},
        ],
        "services": [
            {"title": "For Advisers", "url": "/adviser/"},
            {"title": "For Institutions", "url": "/institutions/"},
            {"title": "Investment Strategies", "url": "/strategies/"},
            {"title": "Support", "url": "/support/"},
        ],
        "legal": [
            {"title": "Privacy Policy", "url": "/disclosures/privacy/"},
            {"title": "Terms of Service", "url": "/disclosures/terms/"},
            {"title": "Disclosures", "url": "/disclosures/disclosures/"},
            {
                "title": "Form ADV",
                "url": "https://reports.adviserinfo.sec.gov/reports/ADV/316032/PDF/316032.pdf",
            },
        ],
        "connect": [
            {"title": "Contact Us", "url": "/contact/"},
            {"title": "Newsletter", "url": "/newsletter/"},
            {"title": "Blog", "url": "/blog/"},
            {"title": "LinkedIn", "url": "https://linkedin.com/company/ecic"},
        ],
    }

    return Response(footer_links, status=status.HTTP_200_OK)


def site_search(request):
    """Simple site search using Wagtail's built-in search functionality."""
    query_string = request.GET.get("q", "").strip()

    if query_string:
        try:
            # Use Wagtail's search functionality
            search_results = Page.objects.live().search(query_string)

            # Log the query (if Query model is available)
            if Query:
                Query.get(query_string).add_hit()

            # Paginate results
            paginator = Paginator(search_results, 10)
            page_number = request.GET.get("page")
            page_obj = paginator.get_page(page_number)

            context = {
                "query_string": query_string,
                "search_results": page_obj,
                "total_results": paginator.count,
                "page": None,  # Add page=None to prevent template errors
            }
        except Exception as e:
            # If search fails (e.g., in testing with missing FTS tables), fall back to simple filtering
            logger.warning("Search functionality failed, using fallback: %s", e)

            # Simple fallback search on page titles
            pages = Page.objects.live().filter(title__icontains=query_string)
            paginator = Paginator(pages, 10)
            page_number = request.GET.get("page")
            page_obj = paginator.get_page(page_number)

            context = {
                "query_string": query_string,
                "search_results": page_obj,
                "total_results": paginator.count,
                "page": None,  # Add page=None to prevent template errors
            }
    else:
        context = {
            "query_string": "",
            "search_results": None,
            "total_results": 0,
            "page": None,  # Add page=None to prevent template errors
        }

    return render(request, "public_site/search_results.html", context)


def site_search_live(request):
    """Live search endpoint for HTMX - returns partial HTML results."""
    query_string = request.GET.get("q", "").strip()

    # Check if this is an HTMX request
    is_htmx = request.headers.get("HX-Request") == "true"

    if not query_string or len(query_string) < 2:
        # Return empty results for short queries
        return render(
            request,
            "public_site/partials/search_results_live.html",
            {
                "query_string": query_string,
                "search_results": [],
                "total_results": 0,
            },
        )

    try:
        # Use Wagtail's search functionality - limit to 5 results for live search
        search_results = Page.objects.live().search(query_string)[:5]

        # Convert to list to get count without extra query
        results_list = list(search_results)

        context = {
            "query_string": query_string,
            "search_results": results_list,
            "total_results": len(results_list),
            "show_more": len(results_list)
            >= 5,  # Show "View all results" if we hit the limit
        }
    except Exception as e:
        # Fallback to simple title search
        logger.warning("Live search failed, using fallback: %s", e)

        pages = Page.objects.live().filter(title__icontains=query_string)[:5]
        results_list = list(pages)

        context = {
            "query_string": query_string,
            "search_results": results_list,
            "total_results": len(results_list),
            "show_more": len(results_list) >= 5,
        }

    # Return partial template for HTMX
    if is_htmx:
        return render(request, "public_site/partials/search_results_live.html", context)
    # For non-HTMX requests, redirect to full search
    return redirect(f"/search/?q={query_string}")


def current_holdings(request):
    """Current Holdings transparency page showing top holdings and portfolio statistics."""
    context = {
        "page_title": "Current Holdings",
        "page_description": "Transparent disclosure of our current portfolio holdings and statistics",
        "current_theme": request.session.get("theme", "light"),
        # Add any dynamic data here if needed in the future
        "last_updated": "2024-12-31",  # This could be dynamic from a model
        "quarter": "Q4 2024",
    }

    return render(request, "public_site/current_holdings.html", context)


# ============================================================================
# GARDEN PLATFORM VIEWS
# ============================================================================


def garden_overview(request):
    """Garden platform overview with features, login access, and interest registration."""

    # Garden platform features
    garden_features = [
        {
            "title": "Portfolio Intelligence",
            "icon": "📊",
            "description": "Thoughtful portfolio curation and performance understanding with integrated ethical framework.",
            "highlights": [
                "Deep portfolio understanding and performance analytics",
                "Multi-strategy support (Growth, Income, Diversification)",
                "Intelligent rebalancing recommendations and insights",
                "Comprehensive risk assessment with downside protection analysis",
                "Tax-loss harvesting optimization and detailed reporting",
            ],
        },
        {
            "title": "Research Platform",
            "icon": "🔍",
            "description": "Deep research tools for thoughtful analysis and cultivating investment wisdom.",
            "highlights": [
                "Company screening with our full exclusion criteria",
                "AI-enhanced fundamental analysis and valuation models",
                "ESG integration with proprietary ethical scoring framework",
                "Market sentiment analysis and pattern recognition",
                "Curated research reports and analytical summaries",
            ],
        },
        {
            "title": "Client Communication Hub",
            "icon": "💬",
            "description": "Thoughtful client relationship management with intelligent communication tools.",
            "highlights": [
                "Curated client reporting with personalized insights",
                "Meeting scheduling and portfolio review management",
                "Document sharing with secure client portal access",
                "Communication history and relationship tracking",
                "Compliance monitoring and regulatory documentation",
            ],
        },
        {
            "title": "AI-Enhanced Wisdom",
            "icon": "🤖",
            "description": "Intelligent assistance for deeper research, analysis, and learning from patterns.",
            "highlights": [
                "Human-in-the-loop (HITL) quality assurance and learning processes",
                "Thoughtful data curation from multiple sources",
                "Natural language query interface for complex analysis",
                "Pattern recognition for market insights and opportunities",
                "Workflow orchestration that learns from your practice",
            ],
        },
        {
            "title": "Compliance & Risk Stewardship",
            "icon": "🛡️",
            "description": "Thoughtful regulatory compliance and risk understanding with intelligent guidance.",
            "highlights": [
                "Fiduciary standard compliance monitoring and reporting",
                "Intelligent regulatory filing and deadline tracking",
                "Risk assessment with stress testing and scenario analysis",
                "Comprehensive audit trail and documentation management",
                "Privacy protection with PII detection and encryption",
            ],
        },
        {
            "title": "Knowledge Integration Canvas",
            "icon": "🔗",
            "description": "Unified knowledge platform weaving together financial, operational, and market insights.",
            "highlights": [
                "Comprehensive market data feeds with price synchronization",
                "Multi-custodian account aggregation and reconciliation",
                "Document management with Paperless-ngx integration",
                "Knowledge graph for understanding entity relationships and insights",
                "Thoughtful API integrations with Sharadar, SEC EDGAR, and more",
            ],
        },
    ]

    context = {
        "page_title": "Garden Investment Platform",
        "garden_features": garden_features,
        "platform_login_url": "/garden/platform/auth/login/",
        "total_features": len(garden_features),
        "feature_count": len(garden_features),
        "highlights_per_feature": 5,
    }

    return render(request, "public_site/garden_overview.html", context)


@api_view(["POST"])
@permission_classes([AllowAny])
def garden_interest_registration(request):
    """Handle Garden platform interest registration form submissions."""

    try:
        # Use DRF request.data which handles both JSON and form data
        data = request.data

        # Extract form fields
        name = data.get("name", "").strip()
        email = data.get("email", "").strip()
        company = data.get("company", "").strip()
        role = data.get("role", "").strip()
        interest_areas = data.get("interest_areas", [])
        message = data.get("message", "").strip()

        # Basic validation
        if not name or not email:
            return Response(
                {"success": False, "error": "Name and email are required fields."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Email format validation
        import re

        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, email):
            return Response(
                {"success": False, "error": "Please enter a valid email address."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create a support ticket to track Garden interest
        try:
            SupportTicket.objects.create(
                name=name,
                email=email,
                company=company,
                subject=f"Garden Platform Interest - {role if role else 'Professional'}",
                message=f"""Garden Platform Access Request:

Company: {company}
Role: {role}
Interest Areas: {", ".join(interest_areas)}

Message:
{message}""",
                ticket_type="garden_interest",
                priority="high",
                status="open",
            )
        except Exception as e:
            logger.warning("Could not create support ticket for Garden interest: %s", e)

        # Log the registration
        logger.info(
            "Garden interest registration: %s (%s) from %s", name, email, company
        )
        logger.info("Role: %s, Interests: %s", role, ", ".join(interest_areas))
        logger.info("Message: %s", message)

        # Return success response
        return Response(
            {
                "success": True,
                "message": "Thank you for your interest! We will contact you soon to discuss Garden platform access.",
            },
            status=status.HTTP_201_CREATED,
        )

    except json.JSONDecodeError:
        return Response(
            {"success": False, "error": "Invalid request format."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    except Exception:
        # Log error
        logger.exception("Error processing Garden interest registration")

        return Response(
            {
                "success": False,
                "error": "An error occurred processing your request. Please try again.",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([AllowAny])
def media_items_api(request):
    """API endpoint for paginated media items for infinite scroll"""
    try:
        # Get page and per_page parameters
        page = int(request.GET.get("page", 1))
        per_page = int(request.GET.get("per_page", 6))

        # Limit per_page to reasonable values
        per_page = min(max(per_page, 1), 50)

        # Check if this is an HTMX request
        is_htmx = request.headers.get("HX-Request") == "true"

        # Get all media items ordered by featured first, then by date
        media_items = MediaItem.objects.select_related("page").order_by(
            "-featured", "-publication_date"
        )

        # Apply pagination
        paginator = Paginator(media_items, per_page)

        try:
            page_obj = paginator.page(page)
        except Exception:
            # If page is out of range, return empty results
            if is_htmx:
                return HttpResponse("")  # Empty response for HTMX

            return Response(
                {
                    "items": [],
                    "has_next": False,
                    "total_pages": paginator.num_pages,
                    "current_page": page,
                    "total_items": paginator.count,
                },
                status=status.HTTP_200_OK,
            )

        # For HTMX request, return HTML partial
        if is_htmx:
            # Create the next page trigger if there are more pages
            next_page_html = ""
            if page_obj.has_next():
                next_page_html = f"""
                <div id="load-more-trigger"
                     hx-get="/api/media-items/?page={page + 1}&per_page={per_page}"
                     hx-trigger="revealed"
                     hx-target="#articles-container"
                     hx-swap="beforeend"
                     hx-indicator="#loading-indicator"
                     hx-swap-oob="true"
                     class="load-more-trigger">
                </div>
                """

            return render(
                request,
                "public_site/partials/media_items.html",
                {"media_items": page_obj, "next_page_trigger": next_page_html},
            )

        # For regular API request, return JSON
        items = []
        for item in page_obj:
            # Process description to remove HTML tags for API response
            description = item.description
            if description:
                import re

                # Simple HTML tag removal for API
                description = re.sub(r"<[^>]+>", "", description)
                description = description.strip()

            items.append(
                {
                    "id": item.id,
                    "title": item.title,
                    "description": description,
                    "publication": item.publication,
                    "publication_date": (
                        item.publication_date.isoformat()
                        if item.publication_date
                        else None
                    ),
                    "external_url": item.external_url,
                    "featured": item.featured,
                }
            )

        return Response(
            {
                "items": items,
                "has_next": page_obj.has_next(),
                "total_pages": paginator.num_pages,
                "current_page": page,
                "total_items": paginator.count,
            },
            status=status.HTTP_200_OK,
        )

    except ValueError:
        return Response(
            {"error": "Invalid page or per_page parameter"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    except Exception:
        logger.exception("Error in media items API")
        return Response(
            {"error": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def live_stats_api(request):
    """API endpoint for live statistics with HTMX polling"""
    import random

    from django.utils import timezone

    # In a real application, these would come from your database or analytics
    # For demo purposes, we'll show slightly varying numbers
    base_screened = 3000
    base_holdings = 18

    stats = {
        "companies_screened": f"{base_screened + random.randint(0, 50):,}+",
        "excluded_percentage": "57%",
        "active_holdings": str(base_holdings + random.randint(-2, 2)),
        "years_research": "15+",
        "last_updated": timezone.now(),
    }

    # Check if this is an HTMX request
    is_htmx = request.headers.get("HX-Request") == "true"

    if is_htmx:
        # Return just the partial template for HTMX
        return render(request, "public_site/partials/live_stats_data.html", stats)
    # Return JSON for regular API calls
    return JsonResponse(stats)


def notifications_count_api(request):
    """API endpoint for notification count"""
    # In a real app, this would check the user's unread notifications
    # For demo, return a random count
    import random

    count = random.choice(
        [0, 0, 0, 1, 2, 3]
    )  # Mostly 0, occasionally some notifications

    # For HTMX requests, return just the count as HTML
    if request.headers.get("HX-Request") == "true":
        if count > 0:
            return HttpResponse(str(count))
        return HttpResponse("")  # Empty for 0 count

    return JsonResponse({"count": count})


def notifications_api(request):
    """API endpoint for notifications list"""
    # Demo notifications - in production, these would come from your database
    from datetime import timedelta

    from django.utils import timezone

    notifications = [
        {
            "id": 1,
            "content": "New research report available: Q1 2025 Market Analysis",
            "time": timezone.now() - timedelta(hours=2),
            "unread": True,
            "url": "/research/q1-2025-analysis/",
        },
        {
            "id": 2,
            "content": "Portfolio update: AAPL position adjusted",
            "time": timezone.now() - timedelta(days=1),
            "unread": True,
            "url": "/portfolio/updates/",
        },
        {
            "id": 3,
            "content": "Monthly newsletter published",
            "time": timezone.now() - timedelta(days=3),
            "unread": False,
            "url": "/blog/",
        },
    ]

    # For HTMX requests, return partial template
    if request.headers.get("HX-Request") == "true":
        return render(
            request,
            "public_site/partials/notification_list.html",
            {"notifications": notifications},
        )

    return JsonResponse({"notifications": notifications})


def mark_notifications_read_api(request):
    """Mark all notifications as read"""
    if request.method == "POST":
        # In production, update the database to mark notifications as read
        # For demo, just return an empty notification list

        if request.headers.get("HX-Request") == "true":
            return render(
                request,
                "public_site/partials/notification_list.html",
                {"notifications": [], "message": "All notifications marked as read"},
            )

        return JsonResponse({"success": True})

    return JsonResponse({"error": "Method not allowed"}, status=405)


def validate_email_api(request):
    """Validate email address for forms (HTMX endpoint)"""
    if request.method == "POST":
        email = request.POST.get("email", "").strip()

        if not email:
            return HttpResponse('<span class="field-error">Email is required</span>')

        # Basic email validation
        import re

        email_regex = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
        if not re.match(email_regex, email):
            return HttpResponse(
                '<span class="field-error">Please enter a valid email address</span>'
            )

        # Check if email is already in use (for demo, check some common domains)
        blocked_domains = ["tempmail.com", "throwaway.email", "10minutemail.com"]
        domain = email.split("@")[1].lower()
        if domain in blocked_domains:
            return HttpResponse(
                '<span class="field-error">Please use a valid email domain</span>'
            )

        # Success
        return HttpResponse('<span class="field-success">✓ Email is valid</span>')

    return HttpResponse("")


def disclosures_page(request):
    """Disclosures page that loads content from database, external source, or fallback"""
    try:
        # Try to get LegalPage content from database
        from .models import LegalPage

        # Look for a disclosures-related legal page
        legal_page = LegalPage.objects.filter(title__icontains="disclosure").first()

        if not legal_page:
            # Try finding by slug
            legal_page = LegalPage.objects.filter(slug__icontains="disclosure").first()

        if not legal_page:
            # Create content that matches https://ethicic.com/disclosures/
            intro = "<p>Important legal disclosures, privacy policy, and regulatory information for Ethical Capital.</p>"
            content = """
            <h2>Privacy Policy</h2>

            <h3>Who We Are</h3>
            <p>Ethical Capital is registered as Invest Vegan LLC, a Utah registered investment adviser. Our founder and Chief Investment Officer is Sloane Ortel. We are located at 90 N 400 E, Provo, UT 84606.</p>

            <h3>Form Submissions</h3>
            <p>We collect information you provide through form submissions on our website, including your IP address and browser information. This information is used to provide our services and communicate with you about your account and our offerings.</p>

            <h3>Cookies</h3>
            <p>Our website may use cookies to enhance your browsing experience and provide personalized content.</p>

            <h3>Embedded Content from Other Websites</h3>
            <p>Our website may include embedded content (e.g., videos, images, articles, etc.) from other websites. Embedded content from other websites behaves in the exact same way as if you have visited the other website.</p>

            <h3>How Long We Retain Your Data</h3>
            <p>We retain your records for a minimum of 5 years as required by the Investment Advisers Act. We do not sell your data to third parties for any reason. We do transmit data through third party services (Google Workspace mostly) as necessary to provide our services.</p>

            <h2>Additional Disclosures</h2>

            <h3>Website Content Disclaimer</h3>
            <p>The content on this website is for informational purposes only. Opinions expressed herein are solely those of the firm unless otherwise specifically cited. We recommend consulting with qualified advisers before implementing any ideas presented on this website.</p>

            <h3>Registration Information</h3>
            <p>Advisory services are offered through Invest Vegan LLC, a Utah registered investment adviser. We comply with all applicable state jurisdiction requirements. We recommend checking with your state securities regulators for any disciplinary history.</p>

            <h3>Social Media Disclosure</h3>
            <p>Our social media accounts do not represent the entire firm's opinion. Any discussions of securities on our social media platforms are not recommendations to buy, sell, or hold any particular security.</p>

            <h2>Contact Information</h2>
            <p>For questions about this privacy policy or our services:</p>

            <p><strong>Ethical Capital</strong><br>
            90 N 400 E<br>
            Provo, UT 84606<br>
            Phone: <a href="tel:+13476259000">+1 347 625 9000</a><br>
            Email: <a href="mailto:sloane@ethicic.com">sloane@ethicic.com</a></p>
            """

            context = {
                "page_title": "Disclosures",
                "page": {
                    "title": "Disclosures",
                    "intro_text": intro,
                    "content": content,
                    "effective_date": timezone.now().date(),
                    "updated_at": timezone.now().date(),
                },
            }
        else:
            context = {
                "page_title": legal_page.title,
                "page": legal_page,
            }

        return render(request, "public_site/legal_page.html", context)

    except Exception:
        logger.exception("Error loading disclosures page")
        # Fallback with basic content
        context = {
            "page_title": "Disclosures",
            "page": {
                "title": "Disclosures",
                "intro_text": "<p>Important legal disclosures for Ethical Capital.</p>",
                "content": "<p>Please contact us for our current disclosures and privacy policy.</p>",
                "effective_date": None,
                "updated_at": None,
            },
        }
        return render(request, "public_site/legal_page.html", context)


def test_clean_nav(request):
    """Test page for clean navigation system"""
    return render(request, "public_site/test_clean_nav.html")


def test_form(request):
    """Test page for form input debugging"""
    return render(request, "public_site/test_form.html")


@api_view(["POST"])
@permission_classes([AllowAny])
def theme_api(request):
    """API endpoint to save user theme preference"""
    try:
        data = json.loads(request.body)
        theme = data.get("theme", "light")

        # Validate theme value
        if theme not in ["light", "dark"]:
            return JsonResponse({"error": "Invalid theme"}, status=400)

        # Store theme in session for anonymous users
        request.session["theme"] = theme

        return JsonResponse({"success": True, "theme": theme})

    except (json.JSONDecodeError, Exception) as e:
        return JsonResponse({"error": str(e)}, status=400)


@require_http_methods(["GET"])
def check_submission_status(request, submission_id):
    """Check the status of a form submission using its external reference ID."""
    try:
        # First check local database
        try:
            ticket = SupportTicket.objects.get(external_reference=submission_id)
            local_status = {
                "found": True,
                "ticket_id": ticket.id,
                "status": ticket.status,
                "created_at": ticket.created_at.isoformat(),
                "ticket_type": ticket.ticket_type,
            }
        except SupportTicket.DoesNotExist:
            local_status = {"found": False}

        # Try to get status from secure API if available
        api_status = None
        try:
            from public_site.services.platform_client import platform_client

            api_status = platform_client.check_submission_status(submission_id)
        except Exception as e:
            logger.warning(f"Failed to check API submission status: {e}")

        return JsonResponse(
            {
                "submission_id": submission_id,
                "local": local_status,
                "api": api_status,
                "timestamp": timezone.now().isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"Error checking submission status: {e}")
        return JsonResponse({"error": "Unable to check submission status"}, status=500)
# Test error tracking views for PostHog


@require_http_methods(["GET"])
def test_error_tracking_view(request):
    """Test error tracking by generating an error"""
    # Security check - only allow with secret parameter
    secret = request.GET.get('secret')
    if secret != 'test-posthog-errors-2025':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    # Get error type to generate
    error_type = request.GET.get('type', 'exception')
    
    # If we're in debug mode, just return info
    if settings.DEBUG:
        return JsonResponse({
            'status': 'DEBUG mode active',
            'message': 'Errors are not sent to PostHog in DEBUG mode',
            'posthog_configured': bool(settings.POSTHOG_API_KEY),
            'posthog_host': settings.POSTHOG_HOST
        })
    
    # Generate the requested error type
    try:
        if error_type == 'exception':
            raise Exception("Test error from error tracking view")
        elif error_type == 'zerodivision':
            result = 1 / 0
        elif error_type == 'attribute':
            obj = None
            obj.some_attribute
        elif error_type == 'key':
            data = {}
            value = data['missing_key']
        elif error_type == 'type':
            result = "string" + 123
        else:
            return JsonResponse({'error': 'Unknown error type'}, status=400)
    except Exception as e:
        # The middleware should catch this and send to PostHog
        raise  # Re-raise to let middleware handle it
    
    # This should never be reached
    return JsonResponse({'status': 'No error generated'})


@require_http_methods(["GET"])
def test_error_info_view(request):
    """Get information about error tracking configuration"""
    import posthog
    
    return JsonResponse({
        'debug_mode': settings.DEBUG,
        'posthog_configured': bool(settings.POSTHOG_API_KEY),
        'posthog_host': settings.POSTHOG_HOST,
        'posthog_api_key_suffix': f"...{settings.POSTHOG_API_KEY[-4:]}" if settings.POSTHOG_API_KEY else None,
        'middleware_active': 'public_site.middleware.PostHogErrorMiddleware' in settings.MIDDLEWARE,
        'posthog_initialized': bool(getattr(posthog, 'project_api_key', None)),
        'instructions': {
            'test_error': '/test-error-tracking/?secret=test-posthog-errors-2025&type=exception',
            'error_types': ['exception', 'zerodivision', 'attribute', 'key', 'type']
        }
    })


# Simple PostHog test view


@require_http_methods(["GET"])
def test_posthog_simple(request):
    """Test basic PostHog functionality"""
    import posthog
    
    # Security check
    secret = request.GET.get('secret')
    if secret != 'test-posthog-2025':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        # Test 1: Send a simple event
        result1 = posthog.capture(
            'test-user',
            'test_event',
            {
                'test': True,
                'source': 'django_backend'
            }
        )
        
        # Test 2: Send an exception event with minimal properties
        result2 = posthog.capture(
            'test-user',
            '$exception',
            {
                '$exception_type': 'TestError',
                '$exception_message': 'This is a test error from Django'
            }
        )
        
        # Test 3: Send exception with Sentry-like format
        result3 = posthog.capture(
            'test-user',
            '$exception',
            {
                'exception': {
                    'values': [{
                        'type': 'TestError',
                        'value': 'Test error with Sentry format'
                    }]
                }
            }
        )
        
        # Flush to ensure events are sent
        posthog.flush()
        
        return JsonResponse({
            'status': 'success',
            'results': {
                'simple_event': str(result1),
                'exception_minimal': str(result2),
                'exception_sentry': str(result3)
            },
            'posthog_config': {
                'api_key_prefix': posthog.project_api_key[:10] if posthog.project_api_key else None,
                'host': posthog.host
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e),
            'type': type(e).__name__
        }, status=500)


@require_http_methods(["GET"])
def test_posthog_exception_formats(request):
    """Test different PostHog exception formats to see which works"""
    import posthog
    
    # Security check
    secret = request.GET.get('secret')
    if secret != 'test-formats-2025':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    results = []
    
    try:
        # Format 1: Using captureException method (if available)
        try:
            error = Exception("Test error using captureException")
            posthog.captureException(error)
            results.append("captureException: Success")
        except AttributeError:
            results.append("captureException: Method not available")
        
        # Format 2: Standard $exception format
        result2 = posthog.capture(
            str(request.user.id) if request.user.is_authenticated else 'anonymous',
            '$exception',
            {
                '$exception_type': 'TestError',
                '$exception_message': 'Test error with standard format',
                '$exception_list': [{
                    'type': 'TestError',
                    'value': 'Test error with standard format',
                    'stacktrace': {
                        'frames': [{
                            'filename': 'test.py',
                            'function': 'test_function',
                            'lineno': 42
                        }]
                    }
                }]
            }
        )
        results.append(f"Standard format: {result2[0]}")
        
        # Format 3: With fingerprint for grouping
        result3 = posthog.capture(
            str(request.user.id) if request.user.is_authenticated else 'anonymous',
            '$exception',
            {
                '$exception_type': 'TestError',
                '$exception_message': 'Test error with fingerprint',
                '$exception_fingerprint': ['test-error-group'],
                '$exception_list': [{
                    'type': 'TestError',
                    'value': 'Test error with fingerprint'
                }]
            }
        )
        results.append(f"With fingerprint: {result3[0]}")
        
        # Format 4: Minimal format
        result4 = posthog.capture(
            str(request.user.id) if request.user.is_authenticated else 'anonymous',
            '$exception',
            {
                'exception': 'Minimal test error'
            }
        )
        results.append(f"Minimal format: {result4[0]}")
        
        # Flush all events
        posthog.flush()
        
        return JsonResponse({
            'status': 'success',
            'results': results,
            'message': 'Check PostHog dashboard in Events and Error Tracking sections'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e)
        }, status=500)


@api_view(["GET"])
@permission_classes([AllowAny])
def performance_chart_data_api(request):
    """API endpoint for investment performance chart data"""
    try:
        from .models import StrategyPage
        from .utils.performance_calculator import parse_percentage, compound_returns
        from datetime import date, datetime
        
        # Get strategy slug from query parameter
        strategy_slug = request.GET.get('strategy', 'growth') if hasattr(request, 'GET') and request.GET else 'growth'
        
        try:
            strategy = StrategyPage.objects.get(slug=strategy_slug)
        except StrategyPage.DoesNotExist:
            # Fall back to first available strategy
            strategy = StrategyPage.objects.first()
            if not strategy:
                return JsonResponse({'error': 'No strategies available'}, status=404)
        
        if not strategy.monthly_returns:
            return JsonResponse({'error': 'No performance data available'}, status=404)
        
        # Process monthly returns into cumulative growth data
        chart_data = []
        benchmark_data = []
        labels = []
        
        # Starting investment amount
        investment_amount = 10000
        cumulative_strategy = investment_amount
        cumulative_benchmark = investment_amount
        
        # Sort years and months chronologically
        months_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                       'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        # Get all year/month combinations sorted chronologically
        data_points = []
        for year_str, year_data in strategy.monthly_returns.items():
            year = int(year_str)
            for month_name, month_data in year_data.items():
                if month_name in months_order:
                    month_index = months_order.index(month_name)
                    data_points.append((year, month_index, month_name, month_data))
        
        # Sort by year and month
        data_points.sort(key=lambda x: (x[0], x[1]))
        
        # Add starting point
        if data_points:
            first_year, first_month_idx, first_month, _ = data_points[0]
            start_date = date(first_year, first_month_idx + 1, 1)
            # Add a point one month before the first data point for the starting $10k
            if first_month_idx > 0:
                prev_month_idx = first_month_idx - 1
                prev_year = first_year
            else:
                prev_month_idx = 11
                prev_year = first_year - 1
            
            prev_month_name = months_order[prev_month_idx]
            labels.append(f"{prev_month_name} {prev_year}")
            chart_data.append(investment_amount)
            benchmark_data.append(investment_amount)
        
        # Process each month's data
        for year, month_index, month_name, month_data in data_points:
            strategy_return_str = month_data.get('strategy', '0%')
            benchmark_return_str = month_data.get('benchmark', '0%')
            
            # Parse percentage returns
            strategy_return = parse_percentage(strategy_return_str)
            benchmark_return = parse_percentage(benchmark_return_str)
            
            # Apply returns to cumulative values
            cumulative_strategy *= (1 + strategy_return)
            cumulative_benchmark *= (1 + benchmark_return)
            
            # Create label
            labels.append(f"{month_name} {year}")
            chart_data.append(round(cumulative_strategy, 2))
            benchmark_data.append(round(cumulative_benchmark, 2))
        
        # Prepare response data
        response_data = {
            'strategy_name': strategy.title,
            'strategy_label': getattr(strategy, 'strategy_label', 'Strategy'),
            'inception_date': strategy.inception_date.isoformat() if strategy.inception_date else None,
            'labels': labels,
            'datasets': [
                {
                    'label': f'{strategy.title} Strategy',
                    'data': chart_data,
                    'borderColor': '#8B5CF6',  # Tailwind purple-500
                    'backgroundColor': 'rgba(139, 92, 246, 0.1)',
                    'fill': False,
                    'tension': 0.2,
                    'borderWidth': 3,
                    'pointBackgroundColor': '#8B5CF6',
                    'pointBorderColor': '#FFFFFF',
                    'pointBorderWidth': 2,
                    'pointRadius': 4,
                    'pointHoverRadius': 6
                },
                {
                    'label': 'Benchmark (S&P 500)',
                    'data': benchmark_data,
                    'borderColor': '#64748B',  # Tailwind slate-500
                    'backgroundColor': 'rgba(100, 116, 139, 0.1)',
                    'fill': False,
                    'tension': 0.2,
                    'borderWidth': 2,
                    'pointBackgroundColor': '#64748B',
                    'pointBorderColor': '#FFFFFF',
                    'pointBorderWidth': 2,
                    'pointRadius': 3,
                    'pointHoverRadius': 5,
                    'borderDash': [5, 5]
                }
            ],
            'performance_summary': {
                'final_strategy_value': round(cumulative_strategy, 2),
                'final_benchmark_value': round(cumulative_benchmark, 2),
                'strategy_total_return': round(((cumulative_strategy / investment_amount) - 1) * 100, 2),
                'benchmark_total_return': round(((cumulative_benchmark / investment_amount) - 1) * 100, 2),
                'outperformance': round(cumulative_strategy - cumulative_benchmark, 2),
                'outperformance_percent': round((cumulative_strategy / cumulative_benchmark - 1) * 100, 2)
            }
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Error in performance_chart_data_api: {str(e)}")
        return JsonResponse({'error': 'Failed to fetch performance data'}, status=500)
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
                ticket_type="contact",
                status="new",
            )

            logger.info(
                "Contact form submitted successfully, created ticket #%s", ticket.id
            )

            # Optional: Still try to submit to main platform API if available
            try:
                api_url = getattr(settings, "MAIN_PLATFORM_API_URL", None)
                if api_url and requests:
                    submission_data = {
                        "first_name": first_name,
                        "last_name": last_name,
                        "email": contact_data["email"],
                        "subject": ticket.subject,
                        "message": contact_data["message"],
                        "category": contact_data["subject"],
                        "company": contact_data.get("company", ""),
                        "source": "public_website",
                    }

                    response = requests.post(
                        f"{api_url}contact/submit/",
                        json=submission_data,
                        timeout=5,  # Shorter timeout since this is optional
                        headers={"Content-Type": "application/json"},
                    )

                    if response.status_code == 201:
                        logger.info("Also submitted to main platform API successfully")
                    else:
                        logger.info(
                            "Main platform API submission failed (non-critical): %s",
                            response.status_code,
                        )

            except Exception as e:
                logger.info("Main platform API submission failed (non-critical): %s", e)
                # Use fallback email as backup notification method
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
        error_messages = []
        for field, errors in form.errors.items():
            for error in errors:
                error_messages.append(f"{field}: {error}")

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
                            contact.notes or ""
                        ) + f"\nRe-subscribed to newsletter on {timezone.now().date()}"
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


@require_http_methods(["POST"])
def onboarding_form_submit(request):
    """Handle comprehensive onboarding form submissions"""
    form = OnboardingForm(request.POST)

    # Check if this is an HTMX request
    is_htmx = request.headers.get("HX-Request") == "true"

    if form.is_valid():
        form_data = form.cleaned_data

        try:
            # Create basic support ticket for onboarding
            full_name = f"{form_data['first_name']} {form_data['last_name']}"

            ticket = SupportTicket.objects.create(
                name=full_name,
                email=form_data["email"],
                subject=f"Onboarding Application - {full_name}",
                message=f"Onboarding application submitted with ${float(form_data['initial_investment']):,.0f} initial investment",
                ticket_type="onboarding",
                status="new",
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
        if is_htmx:
            return render(
                request,
                "public_site/partials/onboarding_error.html",
                {
                    "message": "Please correct the following errors:",
                    "errors": form.errors,
                },
            )

        error_messages = []
        for field, errors in form.errors.items():
            for error in errors:
                error_messages.append(f"{field}: {error}")

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
                ticket_type="contact",
                status="new",
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

            navigation = []
            for page in nav_pages:
                navigation.append(
                    {
                        "title": page.title,
                        "url": page.url,
                        "slug": page.slug,
                    },
                )

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
            }
    else:
        context = {
            "query_string": "",
            "search_results": None,
            "total_results": 0,
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
                status="new",
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
                    "publication_date": item.publication_date.isoformat()
                    if item.publication_date
                    else None,
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

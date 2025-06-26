"""Public Site Views - API endpoints and form handling for Wagtail-based public site
Provides REST API views for contact forms, newsletter signup, and support functionality
"""

import json
import logging

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db import transaction
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from wagtail.models import Page

# Import CRM models and choices for contact classification
from crm.models import Contact
from crm.models.choices import ContactStatus, ContactType, PriorityLevel

from .forms import (
    AccessibleContactForm,
    AccessibleNewsletterForm,
    OnboardingForm,
)


# Models are accessed via API calls to main platform


logger = logging.getLogger(__name__)


def send_fallback_email(contact_data):
    """Send email when API is unavailable"""
    if hasattr(settings, "CONTACT_EMAIL") and settings.CONTACT_EMAIL:
        try:
            send_mail(
                subject=f"New Contact Form: {contact_data['subject']}",
                message=f"""
New contact form submission from public website:

Name: {contact_data["name"]}
Email: {contact_data["email"]}
Company: {contact_data.get("company", "Not provided")}
Subject: {contact_data["subject"]}

Message:
{contact_data["message"]}

NOTE: This was submitted via email fallback because the main platform API
was unavailable.
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.CONTACT_EMAIL],
                fail_silently=True,
            )
        except Exception:
            logger.exception("Failed to send fallback contact form email")


# ============================================================================
# FORM HANDLING VIEWS
# ============================================================================


@require_http_methods(["POST"])
def contact_form_submit(request):
    """Handle contact form submissions from public site via API calls
    """
    form = AccessibleContactForm(request.POST)

    if form.is_valid():
        # Process the form data
        contact_data = form.cleaned_data

        try:
            # Submit to main platform API
            api_url = getattr(
                settings, 'MAIN_PLATFORM_API_URL', 'http://web:8000/api/v1/'
            )

            # Prepare data for API submission
            submission_data = {
                'first_name': (
                    contact_data["name"].split()[0] if contact_data["name"] else ""
                ),
                'last_name': (
                    " ".join(contact_data["name"].split()[1:])
                    if len(contact_data["name"].split()) > 1 else ""
                ),
                'email': contact_data["email"],
                'subject': (
                    f"{contact_data['subject']} - "
                    f"{contact_data.get('company', 'Individual')}"
                ),
                'message': contact_data["message"],
                'category': contact_data["subject"],
                'company': contact_data.get("company", ""),
                'source': 'public_website'
            }

            # Try to submit to main platform API
            import requests
            try:
                response = requests.post(
                    f"{api_url}contact/submit/",
                    json=submission_data,
                    timeout=10,
                    headers={'Content-Type': 'application/json'}
                )

                if response.status_code == 201:
                    logger.info(
                        f"Contact form submitted successfully to API: {response.json()}"
                    )
                else:
                    logger.warning(
                        f"API submission failed with status {response.status_code}: "
                        f"{response.text}"
                    )
                    # Fall back to email if API fails
                    send_fallback_email(contact_data)

            except requests.RequestException:
                logger.exception("Failed to submit to API")
                # Fall back to email if API is unavailable
                send_fallback_email(contact_data)

            messages.success(
                request,
                "Thank you for your message! We will get back to you within 24 hours.",
            )

            # Redirect back to contact page
            return redirect("/contact/")

        except Exception:
            logger.exception("Error processing contact form")
            messages.error(
                request,
                (
                    "There was an error processing your request. Please try again "
                    "or email us directly."
                ),
            )
            return redirect("/contact/")

    else:
        # Form has errors - redirect back with error message
        error_messages = []
        for field, errors in form.errors.items():
            for error in errors:
                error_messages.append(f"{field}: {error}")

        messages.error(
            request,
            f"Please correct the following errors: {', '.join(error_messages)}",
        )
        return redirect("/contact/")


@require_http_methods(["POST"])
def newsletter_signup(request):
    """Handle newsletter signup submissions
    """
    form = AccessibleNewsletterForm(request.POST)

    if form.is_valid():
        email = form.cleaned_data["email"]

        try:
            # Here you would integrate with your email service provider
            # For example: Mailchimp, ConvertKit, etc.

            # Log the signup
            logger.info(f"Newsletter signup: {email}")

            # Create a simple support ticket to track newsletter signups
            SupportTicket.objects.create(
                first_name="Newsletter",
                last_name="Subscriber",
                email=email,
                subject="Newsletter Signup",
                message="Newsletter subscription request",
                category="general",
                status="resolved",
            )

            messages.success(
                request,
                "Thank you for subscribing! You will receive our newsletter updates.",
            )

        except Exception:
            logger.exception("Error processing newsletter signup")
            messages.error(
                request, "There was an error with your subscription. Please try again.",
            )

    else:
        messages.error(request, "Please provide a valid email address.")

    # Redirect back to the page they came from
    return redirect(request.META.get("HTTP_REFERER", "/"))


def classify_contact_priority(form_type, form_data):
    """Classify contact priority and status based on engagement AND business criteria.

    Contact Status Logic:
    - COLD_LEAD: Initial contact, imported data, no engagement
    - WARM_LEAD: Shows active interest (forms, inquiries)
    - PROSPECT: Strong interest (onboarding, partnership inquiries)
    - CLIENT: Actually investing money with us
    - FRIEND: Personal/professional network, not business prospect

    Key Insight: AUM/credentials alone don't equal engagement!
    Status is based on ACTIONS they've taken, not just who they are.

    Prioritizes:
    1. Active engagement over static credentials
    2. Investment advisers and RIAs (when they engage)
    3. Institutional contacts (when they engage)
    4. Business initiative (reaching out vs. being imported)
    """
    importance_score = 0.5  # Default
    priority_level = PriorityLevel.MEDIUM
    contact_status = ContactStatus.COLD_LEAD  # Default to cold lead

    email = form_data.get('email', '').lower()
    company = form_data.get('company', '').lower()
    job_title = (
        form_data.get('role', '').lower() or
        form_data.get('job_title', '').lower()
    )
    subject = form_data.get('subject', '').lower()
    message = form_data.get('message', '').lower()

    # Business email domains get higher priority
    business_domains = [
        '.edu', '.org', '.gov',  # Institutional
        'advisors.com', 'investment', 'capital', 'wealth', 'asset',  # Finance
    ]
    personal_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']

    is_business_email = any(domain in email for domain in business_domains)
    is_personal_email = any(domain in email for domain in personal_domains)

    # Investment adviser indicators
    adviser_keywords = [
        'ria', 'investment advisor', 'investment adviser', 'financial advisor',
        'portfolio manager', 'wealth manager', 'cio', 'chief investment officer',
        'advisor', 'adviser', 'schwab', 'fidelity', 'td ameritrade', 'custody'
    ]

    # Institutional indicators
    institutional_keywords = [
        'endowment', 'foundation', 'pension', 'university', 'college',
        'fund', 'trust', 'institutional', 'fiduciary', 'committee'
    ]

    # Check for adviser indicators
    is_adviser = any(keyword in job_title for keyword in adviser_keywords) or \
                any(keyword in company for keyword in adviser_keywords) or \
                any(keyword in subject for keyword in adviser_keywords) or \
                any(keyword in message for keyword in adviser_keywords)

    # Check for institutional indicators
    is_institutional = any(keyword in job_title for keyword in institutional_keywords) or \
                      any(keyword in company for keyword in institutional_keywords) or \
                      any(keyword in subject for keyword in institutional_keywords) or \
                      any(keyword in message for keyword in institutional_keywords)

    # Assets under management from form data
    aum = form_data.get('assets_under_management', '')
    initial_investment = form_data.get('initial_investment', 0)

    # Contact status based on ENGAGEMENT first, then credentials

    # High engagement activities = immediate status upgrade
    if form_type == 'onboarding':
        # Onboarding = strong interest = prospect status
        contact_status = ContactStatus.PROSPECT
        if initial_investment >= 500000:
            importance_score = 0.95
            priority_level = PriorityLevel.CRITICAL
        elif initial_investment >= 100000:
            importance_score = 0.85
            priority_level = PriorityLevel.HIGH
        else:
            importance_score = 0.75
            priority_level = PriorityLevel.HIGH

    elif form_type == 'contact_form':
        # ANY contact form = warm lead (took initiative to reach out)
        contact_status = ContactStatus.WARM_LEAD

        # Boost importance if they have good credentials AND took action
        if is_institutional:
            importance_score = 0.95
            priority_level = PriorityLevel.CRITICAL
            if 'partnership' in form_data.get('subject', '').lower():
                contact_status = ContactStatus.PROSPECT  # Partnership inquiry = prospect
        elif is_adviser:
            importance_score = 0.90
            priority_level = PriorityLevel.HIGH
            if 'partnership' in form_data.get('subject', '').lower():
                contact_status = ContactStatus.PROSPECT  # Partnership inquiry = prospect
        elif aum and ('100m' in aum or '500m' in aum or '1b' in aum or 'over' in aum):
            importance_score = 0.85
            priority_level = PriorityLevel.HIGH
        elif aum and ('50m' in aum or '10m' in aum):
            importance_score = 0.75
            priority_level = PriorityLevel.HIGH
        elif is_business_email and not is_personal_email:
            importance_score = 0.65
            priority_level = PriorityLevel.MEDIUM
        else:
            importance_score = 0.60
            priority_level = PriorityLevel.MEDIUM

    elif form_type == 'newsletter':
        # Newsletter = cold lead (minimal engagement)
        contact_status = ContactStatus.COLD_LEAD
        importance_score = 0.30
        priority_level = PriorityLevel.LOW

    elif form_type in {'import', 'bulk_import'}:
        # Imported contacts = cold lead regardless of credentials
        # They haven't engaged with us yet, even if they're impressive
        contact_status = ContactStatus.COLD_LEAD

        # But set importance score based on potential
        if is_institutional:
            importance_score = 0.85  # High potential, but no engagement yet
            priority_level = PriorityLevel.HIGH
        elif is_adviser:
            importance_score = 0.80  # High potential, but no engagement yet
            priority_level = PriorityLevel.HIGH
        elif aum and ('100m' in aum or '500m' in aum or '1b' in aum or 'over' in aum):
            importance_score = 0.75  # Good potential
            priority_level = PriorityLevel.MEDIUM
        elif aum and ('50m' in aum or '10m' in aum):
            importance_score = 0.65  # Medium potential
            priority_level = PriorityLevel.MEDIUM
        elif is_business_email and not is_personal_email:
            importance_score = 0.55  # Some potential
            priority_level = PriorityLevel.MEDIUM
        else:
            importance_score = 0.40  # Basic contact
            priority_level = PriorityLevel.LOW

    else:
        # Unknown form type - default to cold lead
        contact_status = ContactStatus.COLD_LEAD
        importance_score = 0.50
        priority_level = PriorityLevel.MEDIUM

    return contact_status, priority_level, importance_score


def create_or_update_contact(email, form_data, form_type, user=None):
    """Create or update CRM contact with business-focused deduplication and classification."""

    # Get contact classification
    contact_status, priority_level, importance_score = classify_contact_priority(form_type, form_data)

    # Try to find existing contact
    contact = Contact.objects.filter(email=email).first()
    created = False

    if contact:
        # Update existing contact with new information (don't overwrite better data)
        if form_data.get('name') and not contact.full_name:
            contact.full_name = form_data['name']
        if form_data.get('first_name') and not contact.first_name:
            contact.first_name = form_data['first_name']
        if form_data.get('last_name') and not contact.last_name:
            contact.last_name = form_data['last_name']
        if form_data.get('company') and not contact.company:
            contact.company = form_data['company']
        if form_data.get('role') and not contact.job_title:
            contact.job_title = form_data['role']
        if form_data.get('phone') and not contact.phone_primary:
            contact.phone_primary = form_data['phone']

        # Always update scores if they're higher (never downgrade)
        if importance_score > contact.importance_score:
            contact.importance_score = importance_score
            contact.priority_level = priority_level

        # Upgrade status if appropriate (never downgrade)
        status_hierarchy = {
            ContactStatus.COLD_LEAD: 1,
            ContactStatus.WARM_LEAD: 2,
            ContactStatus.PROSPECT: 3,
            ContactStatus.CLIENT: 4,
            ContactStatus.FORMER_CLIENT: 3,  # Can upgrade former client to client
            ContactStatus.FRIEND: 1,  # Friends stay friends unless they become business prospects
        }

        current_level = status_hierarchy.get(contact.status, 1)
        new_level = status_hierarchy.get(contact_status, 1)

        if new_level > current_level:
            contact.status = contact_status

        contact.last_interaction = timezone.now()
        contact.interaction_count += 1

    else:
        # Create new contact
        created = True
        full_name = form_data.get('name') or f"{form_data.get('first_name', '')} {form_data.get('last_name', '')}".strip()

        contact = Contact.objects.create(
            email=email,
            full_name=full_name,
            first_name=form_data.get('first_name', ''),
            last_name=form_data.get('last_name', ''),
            company=form_data.get('company', ''),
            job_title=form_data.get('role', ''),
            phone_primary=form_data.get('phone', ''),
            status=contact_status,
            priority_level=priority_level,
            importance_score=importance_score,
            engagement_score=0.5,  # Default
            influence_score=0.5,  # Default
            last_interaction=timezone.now(),
            interaction_count=1,
            source=f'website_{form_type}',
            created_by=user,
        )

        # Determine contact type based on form data
        if form_data.get('company'):
            contact.contact_type = ContactType.COMPANY
        else:
            contact.contact_type = ContactType.INDIVIDUAL

    # Store form-specific data in custom_fields
    if not contact.custom_fields:
        contact.custom_fields = {}

    contact.custom_fields[f'{form_type}_submission'] = {
        'date': timezone.now().isoformat(),
        'data': {k: v for k, v in form_data.items() if k not in ['email', 'first_name', 'last_name', 'name', 'company', 'role', 'phone']}
    }

    contact.save()

    return contact, created


@require_http_methods(["POST"])
def onboarding_form_submit(request):
    """Handle comprehensive onboarding form submissions with CRM integration
    """
    form = OnboardingForm(request.POST)

    if form.is_valid():
        form_data = form.cleaned_data

        try:
            with transaction.atomic():
                # Create or update CRM Contact with highest priority for onboarding
                full_name = f"{form_data['first_name']} {form_data['last_name']}"
                form_data['name'] = full_name  # Add for compatibility with create_or_update_contact

                contact, created = create_or_update_contact(
                    email=form_data["email"],
                    form_data=form_data,
                    form_type='onboarding'
                )

                # Update contact with comprehensive onboarding data
                contact.first_name = form_data['first_name']
                contact.last_name = form_data['last_name']
                contact.full_name = full_name
                contact.phone_primary = form_data.get('phone', '')

                # Classification based on investment amount
                initial_investment = form_data['initial_investment']
                if initial_investment >= 500000:
                    contact.status = ContactStatus.CLIENT  # High-value onboarding = likely client
                    contact.priority_level = PriorityLevel.CRITICAL
                    contact.importance_score = 0.95
                elif initial_investment >= 100000:
                    contact.priority_level = PriorityLevel.HIGH
                    contact.importance_score = 0.85
                else:
                    contact.importance_score = 0.75

                # Store comprehensive onboarding information in custom_fields
                if not contact.custom_fields:
                    contact.custom_fields = {}

                contact.custom_fields['onboarding_application'] = {
                    'location': form_data['location'],
                    'investment_goals': {
                        'primary_goal': form_data['primary_goal'],
                        'time_horizon': form_data['time_horizon'],
                        'initial_investment': str(initial_investment),
                        'monthly_contribution': str(form_data.get('monthly_contribution', 0)),
                    },
                    'ethical_preferences': {
                        'exclusions': form_data.get('exclusions', []),
                        'impact_areas': form_data.get('impact_areas', []),
                    },
                    'experience_level': form_data['experience_level'],
                    'submission_date': timezone.now().isoformat(),
                    'application_status': 'submitted',
                }

                contact.save()

                # Create high-value interaction record
                ContactInteraction.objects.create(
                    contact=contact,
                    interaction_type=InteractionType.DOCUMENT,
                    subject=f"Onboarding Application - ${initial_investment:,.0f} Initial Investment",
                    description=f"Onboarding application submitted for ${initial_investment:,.2f} initial investment",
                    interaction_date=timezone.now(),
                    engagement_impact=0.9,  # Very high engagement for full onboarding
                )

                messages.success(
                    request,
                    "Thank you for your application! We have received your information and will review it shortly."
                )

                return redirect("/onboarding/thank-you/")

        except Exception:
            logger.exception("Error processing onboarding form")
            messages.error(
                request,
                "There was an error processing your application. Please try again or contact us directly."
            )
            return redirect("/onboarding/")

    else:
        # Form has errors
        error_messages = []
        for field, errors in form.errors.items():
            for error in errors:
                error_messages.append(f"{field}: {error}")

        messages.error(
            request, f"Please correct the following errors: {', '.join(error_messages)}",
        )
        return redirect("/onboarding/")


def onboarding_thank_you(request):
    """Thank you page after onboarding application submission
    """
    context = {
        "page_title": "Application Received",
        "heading": "Thank You for Your Application!",
        "message": "We have received your onboarding application and will review it shortly.",
        "next_steps": [
            "Account review and approval (1-2 business days)",
            "Schedule a consultation with your advisor",
            "Fund your account and begin investing",
            "Access your personalized investment dashboard",
        ],
    }

    return render(request, "public_site/onboarding_thank_you.html", context)


# ============================================================================
# API VIEWS
# ============================================================================


@api_view(["POST"])
@permission_classes([AllowAny])
def contact_api(request):
    """API endpoint for contact form submissions
    Returns JSON response for AJAX form submissions
    """
    try:
        data = request.data if hasattr(request, "data") else json.loads(request.body)

        form = AccessibleContactForm(data)

        if form.is_valid():
            contact_data = form.cleaned_data

            with transaction.atomic():
                # Create or update CRM Contact
                contact, created = create_or_update_contact(
                    email=contact_data["email"],
                    form_data=contact_data,
                    form_type='contact_form'
                )

                # Create interaction record
                ContactInteraction.objects.create(
                    contact=contact,
                    interaction_type=InteractionType.EMAIL,
                    subject=f"Contact Form API: {contact_data['subject']}",
                    description=contact_data["message"],
                    interaction_date=timezone.now(),
                    engagement_impact=0.2,  # Positive engagement for form submission
                )

                # Create support ticket (keep existing functionality)
                ticket = SupportTicket.objects.create(
                    first_name=contact.first_name,
                    last_name=contact.last_name,
                    email=contact_data["email"],
                    subject=f"{contact_data['subject']} - {contact_data.get('company', 'Individual')}",
                    message=contact_data["message"],
                    category=contact_data["subject"],
                    status="open",
                )

            # Send notification email (if configured)
            if hasattr(settings, "CONTACT_EMAIL") and settings.CONTACT_EMAIL:
                try:
                    send_mail(
                        subject=f"New Contact Form: {contact_data['subject']}",
                        message=f"""
New contact form submission:

Name: {contact_data["name"]}
Email: {contact_data["email"]}
Company: {contact_data.get("company", "Not provided")}
Subject: {contact_data["subject"]}

Message:
{contact_data["message"]}

Support Ticket ID: {ticket.id}
                        """,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[settings.CONTACT_EMAIL],
                        fail_silently=True,
                    )
                except Exception:
                    logger.exception("Failed to send contact form email")

            return Response(
                {
                    "success": True,
                    "message": "Thank you for your message! We will get back to you within 24 hours.",
                    "ticket_id": ticket.id,
                },
                status=status.HTTP_201_CREATED,
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
    """API endpoint for newsletter signup
    Returns JSON response for AJAX submissions
    """
    try:
        data = request.data if hasattr(request, "data") else json.loads(request.body)

        form = AccessibleNewsletterForm(data)

        if form.is_valid():
            email = form.cleaned_data["email"]
            opt_in = form.cleaned_data.get("opt_in", True)

            with transaction.atomic():
                # Create or update CRM Contact
                contact_data = {
                    'name': email.split('@')[0].replace('.', ' ').title(),  # Fallback name from email
                    'opt_in_marketing': opt_in,
                }
                contact, contact_created = create_or_update_contact(
                    email=email,
                    form_data=contact_data,
                    form_type='newsletter'
                )

                # Set newsletter preferences
                contact.opt_in_marketing = opt_in
                contact.save()

                # Create interaction record
                ContactInteraction.objects.create(
                    contact=contact,
                    interaction_type=InteractionType.EMAIL,
                    subject="Newsletter Subscription (API)",
                    description=f"Newsletter subscription request via API ({'opted in' if opt_in else 'opted out'})",
                    interaction_date=timezone.now(),
                    engagement_impact=0.1,  # Light engagement for newsletter signup
                )

                # Log the signup
                logger.info(f"Newsletter signup via API: {email} (Contact {'created' if contact_created else 'updated'})")

                # Create a simple support ticket to track newsletter signups (keep for legacy)
                SupportTicket.objects.create(
                    first_name=contact.first_name or "Newsletter",
                    last_name=contact.last_name or "Subscriber",
                    email=email,
                    subject="Newsletter Signup",
                    message="Newsletter subscription request via API",
                    category="general",
                    status="resolved",
                )

            return Response(
                {
                    "success": True,
                    "message": "Thank you for subscribing! You will receive our newsletter updates.",
                },
                status=status.HTTP_201_CREATED,
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
    """API endpoint for site status and health check
    Used by monitoring systems and frontend status checks
    """
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
def support_categories_api(request):
    """API endpoint to get available support categories
    Used by frontend forms for dynamic category selection
    """
    try:
        from .models import FAQArticle

        # Get categories from FAQArticle choices
        categories = []
        for value, label in FAQArticle._meta.get_field("category").choices:
            if value:  # Skip empty choice
                categories.append(
                    {
                        "value": value,
                        "label": label,
                        "article_count": FAQArticle.objects.filter(
                            category=value, live=True,
                        ).count(),
                    },
                )

        return Response(
            {
                "categories": categories,
                "total_articles": FAQArticle.objects.filter(live=True).count(),
            },
            status=status.HTTP_200_OK,
        )

    except Exception:
        logger.exception("Error getting support categories")
        return Response(
            {"error": "Unable to load support categories"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# ============================================================================
# UTILITY VIEWS
# ============================================================================


# Demo functionality removed - we provide asset management services, not platform demos


def contact_success(request):
    """Contact form success page
    """
    context = {
        "page_title": "Message Sent",
        "heading": "Thank You for Contacting Us!",
        "message": "We have received your message and will respond within 24 hours.",
    }

    return render(request, "public_site/contact_success.html", context)


# ============================================================================
# WAGTAIL PAGE CONTEXT HELPERS
# ============================================================================


@api_view(["GET"])
@permission_classes([AllowAny])
def get_site_navigation(request):
    """API endpoint to get site navigation structure
    Used by templates and frontend for consistent navigation
    """
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

            return Response(
                {"navigation": navigation}, status=status.HTTP_200_OK,
            )

    except Exception:
        logger.exception("Error getting site navigation")

    # Fallback navigation structure
    fallback_navigation = [
        {"title": "Home", "url": "/", "slug": "home"},
        {"title": "About", "url": "/about/", "slug": "about"},
        {"title": "Research", "url": "/research/", "slug": "research"},
        {"title": "Process", "url": "/process/", "slug": "process"},
        {"title": "Pricing", "url": "/pricing/", "slug": "pricing"},
        {"title": "Support", "url": "/support/", "slug": "support"},
        {"title": "Contact", "url": "/contact/", "slug": "contact"},
    ]

    return Response(
        {"navigation": fallback_navigation}, status=status.HTTP_200_OK,
    )


def site_search(request):
    """Site-wide search using Wagtail's search functionality
    """
    search_query = request.GET.get('q', '').strip()
    page = request.GET.get('page', 1)

    # Initialize empty results
    search_results = Page.objects.none()

    if search_query:
        # Search all live, public pages using Wagtail search
        search_results = Page.objects.live().public().search(search_query)

        # Log the search query for analytics
        # TODO: Fix Query import for search analytics
        # query_object = Query.get(search_query)
        # query_object.add_hit()

    # Paginate results
    paginator = Paginator(search_results, 10)  # 10 results per page
    try:
        page_obj = paginator.page(page)
    except Exception:
        page_obj = paginator.page(1)

    context = {
        'search_query': search_query,
        'search_results': page_obj,
        'paginator': paginator,
        'total_results': paginator.count if search_query else 0,
    }

    return render(request, 'public_site/search_results.html', context)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_footer_links(request):
    """API endpoint to get footer link structure
    """
    footer_links = {
        "company": [
            {"title": "About Us", "url": "/about/"},
            {"title": "Our Process", "url": "/process/"},
            {"title": "Research Methodology", "url": "/research/"},
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
            {"title": "Form ADV", "url": "https://reports.adviserinfo.sec.gov/reports/ADV/316032/PDF/316032.pdf"},
        ],
        "connect": [
            {"title": "Contact Us", "url": "/contact/"},
            {"title": "Newsletter", "url": "/newsletter/"},
            {"title": "Blog", "url": "/blog/"},
            {"title": "LinkedIn", "url": "https://linkedin.com/company/ecic"},
        ],
    }

    return Response(footer_links, status=status.HTTP_200_OK)

"""
Homepage view that renders content from the CMS instead of hardcoded values
"""

from django.http import Http404
from django.shortcuts import render
from wagtail.models import Site

from public_site.models import HomePage


def homepage_view_cms(request):
    """Render the homepage using content from the CMS"""
    try:
        # Get the current site
        site = Site.find_for_request(request)

        # Try to get the homepage from the site root
        if site and hasattr(site.root_page.specific, "hero_tagline"):
            # The root page is a HomePage
            page = site.root_page.specific
        else:
            # Otherwise, find the first live HomePage
            page = HomePage.objects.live().first()

        if not page:
            raise Http404("No homepage found")

        # Pass the page to the template
        context = {
            "page": page,
            "self": page,  # Wagtail convention
        }

        return render(request, page.template, context)

    except Exception:
        # Fallback to the hardcoded view if there's an error
        from public_site.homepage_view import homepage_view

        return homepage_view(request)

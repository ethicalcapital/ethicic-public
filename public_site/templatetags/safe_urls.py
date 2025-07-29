"""
Safe URL template tags for Wagtail pages.
Provides robust URL generation that handles None values gracefully.
"""

from django import template
from django.utils.safestring import mark_safe
from wagtail.models import Page

register = template.Library()


@register.simple_tag(takes_context=True)
def safe_pageurl(context, page, fallback_url="#"):
    """
    Generate a safe URL for a Wagtail page, handling None values gracefully.

    Args:
        context: Template context
        page: Wagtail Page instance or None
        fallback_url: URL to use if page URL cannot be determined (default: "#")

    Returns:
        str: A valid URL or the fallback URL
    """
    if not page:
        return fallback_url

    if not isinstance(page, Page):
        return fallback_url

    # Try multiple methods to get a valid URL
    url = None

    # Method 1: Try the standard url property
    try:
        url = page.url
        if url and url != "None" and url.strip():
            return url
    except (AttributeError, Exception):
        pass

    # Method 2: Try get_url() method
    try:
        request = context.get("request")
        url = page.get_url(request=request)
        if url and url != "None" and url.strip():
            return url
    except (AttributeError, Exception):
        pass

    # Method 3: Try get_full_url() method
    try:
        request = context.get("request")
        url = page.get_full_url(request=request)
        if url and url != "None" and url.strip():
            return url
    except (AttributeError, Exception):
        pass

    # Method 4: Construct URL from url_path if available
    try:
        if hasattr(page, "url_path") and page.url_path:
            url_path = page.url_path.strip()
            if url_path and url_path != "/":
                # Remove any leading duplicate slashes and ensure single leading slash
                url_path = "/" + url_path.lstrip("/")
                if url_path not in {"None", "/None"}:
                    return url_path
    except (AttributeError, Exception):
        pass

    # Method 5: If all else fails, try to construct from slug and parent
    try:
        if hasattr(page, "slug") and page.slug:
            slug = page.slug.strip()
            if slug and slug != "None":
                # For most pages, we can construct the URL as /slug/
                return f"/{slug}/"
    except (AttributeError, Exception):
        pass

    # Last resort: return fallback URL
    return fallback_url


@register.simple_tag(takes_context=True)
def safe_pageurl_absolute(context, page, fallback_url="#"):
    """
    Generate a safe absolute URL for a Wagtail page.

    Args:
        context: Template context
        page: Wagtail Page instance or None
        fallback_url: URL to use if page URL cannot be determined

    Returns:
        str: A valid absolute URL or the fallback URL
    """
    if not page:
        return fallback_url

    # Get the relative URL first
    relative_url = safe_pageurl(context, page, None)

    if not relative_url or relative_url == "#":
        return fallback_url

    # If it's already absolute, return it
    if relative_url.startswith("http"):
        return relative_url

    # Construct absolute URL
    try:
        request = context.get("request")
        if request:
            # Use request to build absolute URL
            scheme = "https" if request.is_secure() else "http"
            host = request.get_host()
            return f"{scheme}://{host}{relative_url}"
    except (AttributeError, Exception):
        pass

    # Fallback to site domain if available
    try:
        if hasattr(page, "get_site"):
            site = page.get_site()
            if site and hasattr(site, "root_url"):
                return f"{site.root_url.rstrip('/')}{relative_url}"
    except (AttributeError, Exception):
        pass

    return fallback_url


@register.filter
def is_valid_url(url):
    """
    Check if a URL is valid (not None, not empty, not 'None' string).

    Args:
        url: URL string to check

    Returns:
        bool: True if URL is valid, False otherwise
    """
    if not url:
        return False

    if not isinstance(url, str):
        return False

    url = url.strip()
    return not (not url or url in {"None", "#"})


@register.simple_tag
def debug_page_url(page):
    """
    Debug template tag to inspect page URL generation issues.
    Only use during development/debugging.

    Args:
        page: Wagtail Page instance

    Returns:
        str: Debug information about the page's URL properties
    """
    if not page:
        return "Page is None"

    debug_info = []
    debug_info.append(f"Page: {page.title} (ID: {page.id})")

    try:
        debug_info.append(f"page.url: '{page.url}'")
    except Exception as e:
        debug_info.append(f"page.url: ERROR - {e}")

    try:
        debug_info.append(f"page.get_url(): '{page.get_url()}'")
    except Exception as e:
        debug_info.append(f"page.get_url(): ERROR - {e}")

    try:
        debug_info.append(f"page.url_path: '{page.url_path}'")
    except Exception as e:
        debug_info.append(f"page.url_path: ERROR - {e}")

    try:
        debug_info.append(f"page.slug: '{page.slug}'")
    except Exception as e:
        debug_info.append(f"page.slug: ERROR - {e}")

    return mark_safe("<br>".join(debug_info))

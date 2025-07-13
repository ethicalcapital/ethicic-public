"""
Context processors for the public site
"""
import os


def theme_context(request):
    """Add theme information to all template contexts"""
    # Handle cases where session might not exist or doesn't have get method
    theme = "light"
    if hasattr(request, "session") and hasattr(request.session, "get"):
        theme = request.session.get("theme", "light")
    return {"current_theme": theme}


def analytics_context(request):  # noqa: ARG001
    """Add analytics configuration to all template contexts"""
    return {"POSTHOG_API_KEY": os.getenv("POSTHOG_API_KEY", "")}


def turnstile_context(request):  # noqa: ARG001
    """Add Turnstile configuration to all template contexts"""
    return {"TURNSTILE_SITE_KEY": os.getenv("TURNSTILE_SITE_KEY", "")}

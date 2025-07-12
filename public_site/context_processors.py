"""
Context processors for the public site
"""


def theme_context(request):
    """Add theme information to all template contexts"""
    # Handle cases where session might not exist or doesn't have get method (e.g., in tests)
    theme = "light"
    if hasattr(request, "session") and hasattr(request.session, "get"):
        theme = request.session.get("theme", "light")
    return {"current_theme": theme}

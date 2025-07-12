"""
Context processors for the public site
"""


def theme_context(request):
    """Add theme information to all template contexts"""
    return {"current_theme": request.session.get("theme", "light")}

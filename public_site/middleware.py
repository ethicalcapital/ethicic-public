"""
Public Site Security Middleware
"""

from django.utils.deprecation import MiddlewareMixin


class PublicSiteSecurityMiddleware(MiddlewareMixin):
    """Security headers middleware for public site"""

    def process_response(self, request, response):
        """Add security headers to response"""

        # Content Security Policy - includes blob: for Plotly chart exports
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://static.cloudflareinsights.com",
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com",
            "img-src 'self' data: https: blob:",
            "font-src 'self' https://cdn.jsdelivr.net https://fonts.gstatic.com",
            "connect-src 'self' ws: wss:",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'",
        ]
        response["Content-Security-Policy"] = "; ".join(csp_directives)

        # Additional security headers
        response["X-Content-Type-Options"] = "nosniff"
        response["X-Frame-Options"] = "DENY"
        response["X-XSS-Protection"] = "1; mode=block"
        response["Referrer-Policy"] = "strict-origin-when-cross-origin"

        return response

"""
PostHog Error Tracking Middleware
"""
import traceback
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin


class PostHogErrorMiddleware(MiddlewareMixin):
    """Middleware to capture exceptions and send them to PostHog"""
    
    def process_exception(self, request, exception):
        """Capture exceptions and send to PostHog"""
        if settings.DEBUG:
            return None
            
        try:
            import posthog
            
            # Get user info if available
            user_id = None
            user_email = None
            if hasattr(request, 'user') and request.user.is_authenticated:
                user_id = str(request.user.id)
                user_email = request.user.email
            
            # Capture the exception using PostHog's built-in method
            if hasattr(posthog, 'capture_exception'):
                # Use the new capture_exception method if available
                posthog.capture_exception(
                    exception,
                    person_id=user_id or 'anonymous',
                    properties={
                        'request_path': request.path,
                        'request_method': request.method,
                        'request_user_agent': request.META.get('HTTP_USER_AGENT', ''),
                        'request_ip': self.get_client_ip(request),
                        'user_email': user_email,
                        'user_authenticated': request.user.is_authenticated if hasattr(request, 'user') else False,
                    }
                )
            else:
                # Fallback to regular capture for older versions
                posthog.capture(
                    user_id or 'anonymous',
                    '$exception',
                    {
                        '$exception_type': type(exception).__name__,
                        '$exception_message': str(exception),
                        '$exception_stack': traceback.format_exc(),
                        '$exception_personURL': request.build_absolute_uri(),
                        'request_path': request.path,
                        'request_method': request.method,
                        'request_user_agent': request.META.get('HTTP_USER_AGENT', ''),
                        'request_ip': self.get_client_ip(request),
                        'user_email': user_email,
                        'user_authenticated': request.user.is_authenticated if hasattr(request, 'user') else False,
                    }
                )
        except Exception:
            # Don't let PostHog errors break the application
            pass
            
        return None
    
    def get_client_ip(self, request):
        """Get the client's IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
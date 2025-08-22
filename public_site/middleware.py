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
            import logging
            
            logger = logging.getLogger('public_site')
            
            # Get user info if available
            user_id = None
            user_email = None
            if hasattr(request, 'user') and request.user.is_authenticated:
                user_id = str(request.user.id)
                user_email = request.user.email
            
            # Format stack trace frames
            tb_frames = []
            tb = exception.__traceback__
            while tb:
                frame = tb.tb_frame
                tb_frames.append({
                    'filename': frame.f_code.co_filename,
                    'function': frame.f_code.co_name,
                    'lineno': tb.tb_lineno,
                    'raw': f"  File \"{frame.f_code.co_filename}\", line {tb.tb_lineno}, in {frame.f_code.co_name}"
                })
                tb = tb.tb_next
            
            # Log that we're capturing an error
            logger.info(f"Capturing exception {type(exception).__name__} for PostHog")
            logger.debug(f"PostHog project_api_key: {posthog.project_api_key[:10]}...") 
            logger.debug(f"PostHog host: {posthog.host}")
            
            # Capture the exception using $exception event format
            result = posthog.capture(
                user_id or 'anonymous',
                '$exception',
                {
                    '$exception_type': type(exception).__name__,
                    '$exception_message': str(exception),
                    '$exception_personURL': request.build_absolute_uri(),
                    '$exception_list': [{
                        'type': type(exception).__name__,
                        'value': str(exception),
                        'stacktrace': {
                            'frames': tb_frames
                        }
                    }],
                    '$exception_stack_trace_raw': traceback.format_exc(),
                    # Additional context
                    'request_path': request.path,
                    'request_method': request.method,
                    'request_user_agent': request.META.get('HTTP_USER_AGENT', ''),
                    'request_ip': self.get_client_ip(request),
                    'user_email': user_email,
                    'user_authenticated': request.user.is_authenticated if hasattr(request, 'user') else False,
                    'django_view': getattr(request, 'resolver_match', {}).view_name if hasattr(request, 'resolver_match') else None,
                }
            )
            
            # Log capture result
            logger.info(f"PostHog capture result: {result}")
            
            # Force flush to ensure event is sent immediately
            posthog.flush()
            
            # Log successful capture
            logger.info(f"Successfully sent {type(exception).__name__} to PostHog")
        except Exception as posthog_error:
            # Log PostHog errors
            logger.error(f"Failed to send error to PostHog: {posthog_error}")
            import traceback
            logger.error(f"PostHog error traceback: {traceback.format_exc()}")
            
        return None
    
    def get_client_ip(self, request):
        """Get the client's IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
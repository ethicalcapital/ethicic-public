# PostHog Error Tracking Setup

This document describes the PostHog error tracking implementation for the Ethical Capital website.

## Overview

Error tracking is configured for both backend (Python/Django) and frontend (JavaScript) environments. Errors are automatically captured and sent to PostHog for analysis and monitoring.

## Configuration

### Environment Variables

- `POSTHOG_API_KEY`: Your PostHog project API key (default: phc_iPeP4HP7NhtEKJmbwwFt65mjlVJjJb1MLe8RXYwIszc)
- `POSTHOG_HOST`: PostHog API host (default: https://us.i.posthog.com)

### PostHog Initialization

PostHog is initialized in the base template with the following features enabled:
- Error tracking (`capture_exceptions: true`)
- Page view tracking
- Page leave tracking
- Session recording (with input masking for privacy)
- Performance monitoring

## Backend Error Tracking

### Middleware

The `PostHogErrorMiddleware` in `public_site/middleware.py` automatically captures all unhandled Django exceptions and sends them to PostHog with:

- Error type and message
- Full stack trace
- Request details (path, method, user agent, IP)
- User information (if authenticated)

### Testing Backend Errors

Use the management command to test error tracking:

```bash
# Test different error types
python manage.py test_error_tracking --type exception
python manage.py test_error_tracking --type zerodivision
python manage.py test_error_tracking --type attribute
python manage.py test_error_tracking --type key
```

**Note**: Error tracking only runs in production (`DEBUG=False`).

## Frontend Error Tracking

### Automatic Error Capture

JavaScript errors are automatically captured through:

1. **Global error handler**: Catches all JavaScript errors
2. **Unhandled rejection handler**: Catches promise rejections

Both handlers use PostHog's `captureException` method when available, with fallback to standard event capture.

### Manual Error Capture

You can manually capture errors in your JavaScript code:

```javascript
try {
    // Your code here
} catch (error) {
    if (window.posthog && window.posthog.captureException) {
        window.posthog.captureException(error, {
            // Additional context
            component: 'MyComponent',
            action: 'user_action'
        });
    }
}
```

### Testing Frontend Errors

Include the test script in development:

```html
<script src="{% static 'js/test-error-tracking.js' %}"></script>
```

This adds test buttons in development to trigger different error types.

## Viewing Errors in PostHog

1. Log in to your PostHog dashboard
2. Navigate to the "Monitoring" or "Exceptions" section
3. View error details including:
   - Error frequency and trends
   - Stack traces
   - User impact
   - Error grouping

## Privacy Considerations

- Session recording masks all inputs by default
- Password and email fields are specifically masked
- User data is only captured for authenticated users
- IP addresses are captured for debugging but can be anonymized

## Best Practices

1. **Don't catch all errors**: Let PostHog capture unhandled errors for visibility
2. **Add context**: When manually capturing, include relevant context
3. **Test regularly**: Use the test commands to ensure error tracking works
4. **Monitor trends**: Check PostHog regularly for error patterns
5. **Fix promptly**: Address high-frequency or high-impact errors quickly

## Troubleshooting

### Errors not appearing in PostHog

1. Check that `DEBUG=False` in production
2. Verify PostHog API key is correct
3. Check browser console for PostHog initialization errors
4. Ensure middleware is properly configured

### Testing locally

To test error tracking locally:

1. Set `DEBUG=False` temporarily
2. Set PostHog credentials in environment
3. Run test commands or trigger test errors
4. Check PostHog dashboard

## Security

- PostHog credentials should be stored as environment variables
- Don't log sensitive data in error messages
- Review stack traces for sensitive information exposure
- Use PostHog's data retention policies appropriately
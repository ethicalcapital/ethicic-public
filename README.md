# Ethical Capital Public Website

This is the standalone public website for Ethical Capital, built with Django and Wagtail CMS.

## Features

- Wagtail CMS for content management
- Blog and media sections
- Contact forms with email notifications
- Newsletter signup
- Responsive design with Garden UI framework
- Dark/light theme support

## Deployment

This repository is configured for deployment on Kinsta using their Python buildpack system.

### Environment Variables

Required environment variables (set in Kinsta dashboard):

- `SECRET_KEY` - Django secret key (required)
- `DATABASE_URL` - PostgreSQL connection URL (provided by Kinsta)
- `ALLOWED_HOSTS` - Comma-separated list of allowed domains

Optional:
- `DEBUG` - Set to "False" in production (default: False)
- `EMAIL_HOST` - SMTP server for sending emails
- `EMAIL_HOST_USER` - SMTP username
- `EMAIL_HOST_PASSWORD` - SMTP password
- `CONTACT_EMAIL` - Email address for contact form submissions

### Local Development

1. Clone the repository
2. Copy `.env.example` to `.env` and configure
3. Install dependencies: `pip install -r requirements.txt`
4. Run migrations: `python manage.py migrate`
5. Create superuser: `python manage.py createsuperuser`
6. Collect static files: `python manage.py collectstatic`
7. Run development server: `python manage.py runserver`

### Production Deployment

1. Push to GitHub
2. Connect repository to Kinsta
3. Configure environment variables in Kinsta dashboard
4. Deploy

The site uses Gunicorn as the WSGI server (configured in `Procfile`).

## Architecture

- `/ethicic` - Main Django project settings
- `/public_site` - Django app containing views, models, and forms
- `/static` - Garden UI framework and custom CSS/JS
- `/templates` - HTML templates

## License

Proprietary - Ethical Capital LLC
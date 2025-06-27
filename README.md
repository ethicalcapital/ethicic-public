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
- `UBI_DATABASE_URL` - Ubicloud database URL - when set, uses hybrid approach with local cache
- `REDIS_URL` - Redis URL for session/query caching (recommended for production)
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

During deployment, the build script (`build.sh`) will automatically:
- Collect static files
- Run database migrations
- Create admin user (username: `srvo`)
- Set up initial site structure
- Import existing content from Ubicloud database (if `UBI_DATABASE_URL` is set)

### Data Import

The site will automatically attempt to import data from your existing Ubicloud database during deployment. This includes:
- Homepage content
- Blog posts
- Media items
- Recent support tickets

If `UBI_DATABASE_URL` is not set or the import fails, the site will continue with an empty content structure that can be managed through the Wagtail CMS at `/cms/`.

To manually run data import after deployment:
```bash
python manage.py import_from_ubicloud
```

## Architecture

- `/ethicic` - Main Django project settings
- `/public_site` - Django app containing views, models, and forms
- `/static` - Garden UI framework and custom CSS/JS
- `/templates` - HTML templates

### Hybrid Database Architecture

When `UBI_DATABASE_URL` is set, the site uses a hybrid approach:
- **Ubicloud** - Primary database for all writes and source of truth
- **Local SQLite** - Cache for frequently accessed content (pages, blog posts)
- **Redis** - Session storage and query result caching

This approach minimizes database costs while maintaining good performance:
1. All writes go to Ubicloud
2. Common read queries use local cache
3. Cache is automatically synced from Ubicloud
4. Changes are propagated to cache via Django signals

To manually sync the cache:
```bash
python manage.py sync_cache
```

## License

Proprietary - Ethical Capital LLC
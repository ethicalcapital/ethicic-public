# Kinsta App Hosting Deployment Checklist

## ✅ 1. Git Repository
- [x] **Repository**: Connected to GitHub at `https://github.com/ethicalcapital/ethicic-public`
- [x] **Branch**: Using `main` branch
- [x] **Access**: Repository is public

## ✅ 2. Environment Variables
Required environment variables for production:

### Database Configuration
- [ ] `DATABASE_URL` - Kinsta database URL (if using Kinsta database)
- [ ] `UBI_DATABASE_URL` - Ubicloud database URL (primary database)
- [ ] `DB_CA_CERT` or `DB_CA_CERT_PATH` - SSL certificate for database
- [ ] `DB_SSLMODE` - Set to `require` or `verify-full`

### Django Settings
- [ ] `SECRET_KEY` - Django secret key (generate a new one for production!)
- [ ] `DEBUG` - Set to `False` for production
- [ ] `ALLOWED_HOSTS` - Include your Kinsta domain and custom domain

### Optional but Recommended
- [ ] `REDIS_URL` - For caching (if using Redis)
- [ ] Email configuration (`EMAIL_HOST`, `EMAIL_PORT`, etc.)

## ✅ 3. Build Configuration
- [x] **Build Path**: Repository root (.)
- [x] **Dockerfile**: Present at `/Dockerfile`
- [x] **Build Script**: `build.sh` handles static files and initial setup
- [x] **Requirements**: `requirements.txt` for Python dependencies

## ✅ 4. Start Command
- [x] **ENTRYPOINT**: `./runtime_init.sh`
- [x] **CMD**: `gunicorn --bind 0.0.0.0:8080 --workers 2 --timeout 60 ethicic.wsgi:application`
- [x] **Port Binding**: Configured to use `$PORT` environment variable (defaults to 8080)
- [x] **Health Check**: Configured in Dockerfile

## ⚠️ 5. Background Workers and Cron Jobs
- [ ] Currently none configured
- [ ] Consider adding if needed for:
  - Cache warming
  - Database sync from Ubicloud
  - Content updates

## ⚠️ 6. Persistent Storage
- [ ] Media files storage - Currently using local storage
- [ ] Consider adding persistent storage for:
  - `/app/media` - User uploaded files
  - `/app/staticfiles` - Collected static files (optional)

## 🔧 7. Production Settings to Verify

### Security Settings
```python
# In settings.py, ensure these are set for production:
DEBUG = False
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

### Static Files
- [x] `STATIC_URL = '/static/'`
- [x] `STATIC_ROOT` configured
- [x] `collectstatic` runs in build.sh
- [x] WhiteNoise configured for serving static files

### Database
- [x] Hybrid database setup (Ubicloud primary + local cache)
- [x] SSL certificate handling in runtime_init.sh
- [x] Fallback to SQLite if Ubicloud unreachable

## 📋 Pre-Deployment Tasks

1. **Generate Production Secret Key**:
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

2. **Update ALLOWED_HOSTS**:
   - Add your Kinsta app URL: `your-app-name.kinsta.app`
   - Add your custom domain: `ethicic.com`

3. **Test Build Locally**:
   ```bash
   docker build -t ethicic-test .
   docker run -p 8080:8080 ethicic-test
   ```

4. **Verify SSL Certificate**:
   - Ensure `config/ssl/ubicloud-root-ca.pem` is in the repository
   - Or set `DB_CA_CERT` environment variable with certificate content

## 🚀 Deployment Steps

1. **In Kinsta Dashboard**:
   - Create new application
   - Connect GitHub repository
   - Select branch: `main`
   - Choose Dockerfile deployment

2. **Configure Environment Variables**:
   - Add all required variables from section 2
   - Use Kinsta's secrets management for sensitive values

3. **Configure Resources**:
   - Choose appropriate machine type
   - Set scaling if needed

4. **Add Custom Domain** (after deployment):
   - Add your domain in Kinsta dashboard
   - Update DNS records
   - Enable SSL

## 📊 Post-Deployment Verification

- [ ] Application loads without errors
- [ ] Database connection successful
- [ ] Static files loading correctly
- [ ] Admin panel accessible at `/admin/`
- [ ] Content pages loading
- [ ] Contact form working
- [ ] SSL certificate valid

## 🔍 Monitoring

- [ ] Set up application monitoring
- [ ] Configure error tracking (e.g., Sentry)
- [ ] Set up uptime monitoring
- [ ] Configure backup strategy

## 📝 Notes

- The application uses a hybrid database approach with Ubicloud as primary
- Falls back to SQLite if Ubicloud is unreachable
- Static files served via WhiteNoise
- Health check endpoint at `/health/`
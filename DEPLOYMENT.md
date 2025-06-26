# Deployment Instructions

## GitHub Setup

1. **Create GitHub Repository**
   - Go to https://github.com/new
   - Repository name: `ethicic-public`
   - Description: `Ethical Capital public website - Django/Wagtail CMS`
   - Visibility: **Public**
   - **DO NOT** initialize with README, .gitignore, or license

2. **Push to GitHub**
   ```bash
   # If using SSH (recommended):
   git remote add origin git@github.com:YOUR_USERNAME/ethicic-public.git
   
   # Or if using HTTPS:
   git remote add origin https://github.com/YOUR_USERNAME/ethicic-public.git
   
   # Push the code
   git push -u origin main
   ```

## Kinsta Deployment

1. **Connect Repository**
   - Log into Kinsta dashboard
   - Create new application
   - Select "Deploy from GitHub"
   - Connect your `ethicic-public` repository
   - Choose `main` branch

2. **Configure Build Settings**
   - Build command: Leave empty (Kinsta auto-detects)
   - Start command: Leave empty (uses Procfile)
   - Build path: `/` (root)

3. **Environment Variables**
   
   Required variables in Kinsta dashboard:
   
   ```
   SECRET_KEY=<generated-secret-key>
   DATABASE_URL=<provided-by-kinsta>
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   ```
   
   Optional email configuration:
   ```
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   CONTACT_EMAIL=hello@ethicic.com
   ```

4. **Database Setup**
   - Kinsta provides PostgreSQL automatically
   - DATABASE_URL includes all connection details
   - SSL is configured automatically

5. **Post-Deployment**
   
   After first deployment, run these commands in Kinsta's console:
   
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py collectstatic --noinput
   ```

## Domain Configuration

1. **Add Custom Domain**
   - In Kinsta dashboard, go to Domains
   - Add your custom domain
   - Update DNS records as instructed

2. **SSL Certificate**
   - Kinsta provides free SSL certificates
   - Automatically configured for custom domains

## Monitoring

- Check application logs in Kinsta dashboard
- Monitor build logs during deployment
- Set up uptime monitoring if needed

## Troubleshooting

**Build Fails:**
- Check requirements.txt syntax
- Verify all dependencies are listed
- Check build logs for specific errors

**Application Won't Start:**
- Verify Procfile syntax
- Check SECRET_KEY is set
- Verify DATABASE_URL is configured
- Check application logs

**Static Files Not Loading:**
- Run `python manage.py collectstatic`
- Verify WhiteNoise is configured
- Check STATIC_ROOT setting

**Database Connection Issues:**
- DATABASE_URL should be automatically set by Kinsta
- SSL is handled automatically
- Check logs for connection errors
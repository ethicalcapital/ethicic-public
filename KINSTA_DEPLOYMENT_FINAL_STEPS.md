# Kinsta Deployment - Final Steps

## ✅ Current Status

Based on your Kinsta dashboard environment variables, here's what's configured:

### Environment Variables (Already Set)
- ✅ `SECRET_KEY` - Production key configured
- ✅ `DEBUG=false` - Production mode enabled
- ✅ `ALLOWED_HOSTS` - Set to `ethical-capital-public-frezv.kinsta.app,ethicic.com,www.ethicic.com`
- ✅ `UBI_DATABASE_URL` - Ubicloud database configured as primary
- ✅ `DATABASE_URL` - Kinsta PostgreSQL configured (but using SQLite fallback)
- ✅ `DB_CA_CERT` - SSL certificates for Ubicloud configured

### Your App Details
- **Kinsta App URL**: `ethical-capital-public-frezv.kinsta.app`
- **GitHub Repository**: `https://github.com/ethicalcapital/ethicic-public`
- **Branch**: `main`

## 🚀 Final Deployment Steps

### 1. Commit Current Changes
```bash
git add -A
git commit -m "Production configuration ready for Kinsta deployment

- Updated production environment configuration
- All content migrated (95/95 items)
- SSL certificates configured
- Docker build optimized for Kinsta"
git push origin main
```

### 2. In Kinsta Dashboard

1. **Trigger Deployment**:
   - Go to your app in Kinsta dashboard
   - Click "Deploy now" or wait for auto-deployment from the git push

2. **Monitor Build**:
   - Watch the build logs for any errors
   - Build should take 5-10 minutes
   - Look for "Build successful" message

3. **Check Application Logs**:
   - After deployment, check runtime logs
   - Look for successful database connection to Ubicloud
   - Verify static files are being served

### 3. Post-Deployment Verification

Test these endpoints on your Kinsta app:

1. **Health Check**:
   ```
   https://ethical-capital-public-frezv.kinsta.app/health/
   ```
   Should return: `{"status": "healthy", "database": "connected"}`

2. **Homepage**:
   ```
   https://ethical-capital-public-frezv.kinsta.app/
   ```
   Should load the Ethical Capital homepage

3. **Admin Panel**:
   ```
   https://ethical-capital-public-frezv.kinsta.app/cms/
   ```
   Should show the Wagtail login page

4. **Static Files**:
   Check that CSS loads properly on the homepage

### 4. Database Migration (if needed)

If the database needs migration on first deploy:

1. In Kinsta dashboard, go to "Runtime commands"
2. Run: `python manage.py migrate --noinput`
3. Run: `python manage.py collectstatic --noinput`

### 5. Add Custom Domain

Once the app is working on Kinsta's domain:

1. **In Kinsta Dashboard**:
   - Go to "Domains" section
   - Add `ethicic.com` and `www.ethicic.com`
   - Note the DNS records provided

2. **Update DNS Records** (at your domain registrar):
   - Add CNAME record pointing to Kinsta's domain
   - Or use the provided A records

3. **Enable SSL**:
   - Kinsta will automatically provision SSL certificates
   - This may take 10-30 minutes after DNS propagation

### 6. Optional: Email Configuration

If you want to enable email functionality:

1. Generate an app-specific password for Gmail
2. Add these environment variables in Kinsta:
   ```
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_HOST_USER=sloane@ethicic.com
   EMAIL_HOST_PASSWORD=your-app-specific-password
   EMAIL_USE_TLS=True
   DEFAULT_FROM_EMAIL=noreply@ethicic.com
   CONTACT_EMAIL=hello@ethicic.com
   ```

## 🔍 Troubleshooting

### If the build fails:
- Check if all Python dependencies are in `requirements.txt`
- Verify the Dockerfile syntax
- Check build logs for specific errors

### If the app doesn't start:
- Check runtime logs for Python errors
- Verify all environment variables are set
- Check if PORT binding is working

### If database connection fails:
- Verify UBI_DATABASE_URL is correct
- Check if SSL certificate is being recognized
- The app will fall back to SQLite if Ubicloud is unreachable

### If static files don't load:
- Check if `collectstatic` ran during build
- Verify WhiteNoise is configured
- Check browser console for 404 errors

## 📊 Expected Behavior

When everything is working correctly:

1. **Database**: Connects to Ubicloud PostgreSQL with all 95 content items
2. **Fallback**: If Ubicloud is unreachable, uses local SQLite
3. **Static Files**: Served via WhiteNoise
4. **Admin**: Accessible at `/cms/` with your superuser credentials
5. **Content**: All pages, blog posts, FAQs, and encyclopedia entries available

## 🎉 Success Indicators

- ✅ Health check returns healthy status
- ✅ Homepage loads with proper styling
- ✅ All navigation links work
- ✅ Content pages load correctly
- ✅ Admin panel is accessible
- ✅ No 500 errors in logs

## 📝 Notes

- The app uses a hybrid database approach (Ubicloud primary + local cache)
- Static files are served directly by the app via WhiteNoise
- SSL is handled by Kinsta's load balancer
- The app is configured for horizontal scaling if needed

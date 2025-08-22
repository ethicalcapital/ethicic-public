# Media Storage Setup for Production

## Issue
Featured images and other media files are not displaying in production on Kinsta because containerized environments don't have persistent file storage.

## Solution
Configure Cloudflare R2 storage for media files (S3-compatible).

## Important: R2 Public Access

R2 buckets are private by default. To serve images publicly, you need one of these options:

### Option 1: R2 Public Buckets (Recommended)
1. In Cloudflare dashboard, go to R2 > your bucket > Settings
2. Under "Public access", enable "Allow public access"
3. Copy the public URL (format: `https://pub-{hash}.r2.dev`)
4. Set the R2_PUBLIC_URL environment variable

### Option 2: Custom Domain
1. Set up a custom domain for your R2 bucket in Cloudflare
2. Use that domain as R2_PUBLIC_URL

### Option 3: Cloudflare Workers (Advanced)
Create a Worker to proxy R2 requests with proper access control

## Setup Instructions

### 1. R2 Bucket Setup
The R2 bucket is configured:
- Bucket name: `images`
- API Endpoint: `https://483f91afa8e97683223b69b57fd773ae.r2.cloudflarestorage.com`
- Public URL: Must be configured (see above)

### 2. Set Environment Variables in Kinsta

```bash
# Enable R2 storage
USE_R2=true

# R2 credentials (already set in Kinsta)
R2_ACCESS_KEY_ID=your-r2-access-key
R2_SECRET_ACCESS_KEY=your-r2-secret-key

# R2 public URL (REQUIRED - get from Cloudflare dashboard)
# Example: https://pub-abc123.r2.dev
R2_PUBLIC_URL=your-r2-public-url
```

### 3. Upload Existing Media Files

If you have existing media files, you'll need to upload them to S3:

```bash
# From your local development environment
python manage.py collectmedia --upload-to-s3
```

Or manually upload the contents of `/media/` to your S3 bucket.

### 4. Alternative: Local Development

For local development, S3 is not required. The system will use local file storage when `USE_S3=false` (default).

## Testing

After configuration:
1. Upload a new image through Wagtail admin
2. Check that the image URL points to S3
3. Verify the image displays correctly on the frontend

## Troubleshooting

Run the diagnostic command:
```bash
python manage.py check_featured_images
```

This will show:
- Current storage configuration
- Sample image URLs
- Whether files exist and are accessible
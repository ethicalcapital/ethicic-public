# Media Storage Setup for Production

## Issue
Featured images and other media files are not displaying in production on Kinsta because containerized environments don't have persistent file storage.

## Solution
Configure Cloudflare R2 storage for media files (S3-compatible).

## Setup Instructions

### 1. R2 Bucket Setup
The R2 bucket is already configured:
- Bucket name: `images`
- Endpoint: `https://483f91afa8e97683223b69b57fd773ae.r2.cloudflarestorage.com`

### 2. Set Environment Variables in Kinsta

Add these environment variables to your Kinsta app:

```bash
# Enable R2 storage
USE_R2=true

# R2 credentials (already set in Kinsta)
R2_ACCESS_KEY_ID=your-r2-access-key
R2_SECRET_ACCESS_KEY=your-r2-secret-key
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
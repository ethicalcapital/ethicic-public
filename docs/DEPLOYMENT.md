# Deployment System - Static File Cache Management

## Problem Solved
The deployment system now properly handles static file caching and regeneration to ensure CSS/JS changes are immediately reflected after deployment.

## Key Improvements

### 1. **Dockerfile Cache Busting**
- Added build-time marker (`/app/.build_marker`) to detect new builds
- Forces static file regeneration on new container builds

### 2. **Enhanced Runtime Initialization**
- `runtime_init.sh` now force-clears static files on new builds
- Verifies critical CSS files are present
- Provides fallback manual copy if collectstatic fails

### 3. **Docker Volume Management**
- Static files volume can be cleared via `rebuild.sh` script
- Environment variable `FORCE_STATIC_REBUILD=true` forces regeneration

### 4. **Development Tools**
- `rebuild.sh` - Force rebuild without Docker cache
- Environment variable controls for cache management

## Usage

### Normal Deployment
```bash
# Standard deployment (uses Docker cache)
docker-compose up --build -d
```

### Force Static File Rebuild
```bash
# Option 1: Use rebuild script (recommended)
./rebuild.sh

# Option 2: Manual steps
docker-compose down
docker volume rm ethicic-public_static_files
docker-compose build --no-cache
docker-compose up -d

# Option 3: Environment variable
FORCE_STATIC_REBUILD=true docker-compose up --build -d
```

### Debugging Static Files
```bash
# Check container logs
docker-compose logs -f app

# Verify static files in container
docker exec -it ethicic-public-app ls -la staticfiles/css/

# Check specific CSS file
docker exec -it ethicic-public-app tail staticfiles/css/about-page-v2.css
```

## How It Works

1. **Build Time**: Dockerfile creates `.build_marker` with timestamp
2. **Runtime**: `runtime_init.sh` detects new build and clears cached static files
3. **Collection**: Django's `collectstatic` regenerates all static files
4. **Verification**: Script ensures critical CSS files are present
5. **Fallback**: Manual copy if collectstatic fails

## Files Modified
- `Dockerfile` - Added build markers and cache busting
- `runtime_init.sh` - Enhanced static file handling
- `docker-compose.yml` - Added environment controls
- `rebuild.sh` - New development tool

## Environment Variables
- `FORCE_STATIC_REBUILD=true` - Forces static file regeneration
- `DEBUG=False` - Production settings (already configured)

This system ensures that CSS changes (like font size fixes) are immediately deployed without manual intervention.

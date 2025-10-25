# ⚠️ REPOSITORY DEPRECATED

**Status**: DEPRECATED  
**Date**: October 25, 2025  
**Purpose**: Feature inventory and historical reference only

---

## Why This Repository Exists

This repository is **no longer actively maintained** and exists solely as an inventory of features built during previous iterations of similar systems. It should **not** be used as a foundation for new development.

This codebase represents one attempt at building a public-facing website and content management system for Ethical Capital. It is preserved to document what was built, what worked, and what didn't, so future projects can learn from this experience.

---

## Complete Feature Inventory

### 1. Content Management System (Wagtail CMS)

**What it does**: Provides a user-friendly admin interface for non-technical staff to manage website content without touching code.

**Key Components**:
- **7 Primary Page Types**:
  - `HomePage` - Main landing page with hero section, philosophy, and strategy overview
  - `BlogPost` - Blog articles with rich content, tags, categories, and related posts
  - `StrategyPage` - Investment strategy details with performance metrics and portfolio data
  - `FAQPage` - Frequently asked questions with deep linking support
  - `EncyclopediaEntry` - Investment term definitions with difficulty levels (Beginner/Intermediate/Advanced)
  - `AboutPage` - Company information and team bios
  - `InstitutionalPage` - Services for institutional clients

- **Admin Interface**: Full Wagtail CMS at `/cms/` with:
  - Rich text editing with WYSIWYG
  - Media library with automatic image optimization (AVIF, WebP)
  - Document management for PDFs and files
  - Page hierarchy and URL management
  - Publishing workflow with draft/live states

- **Content Features**:
  - StreamField for flexible page layouts
  - Blog system with categories, tags, and search
  - Encyclopedia with 100+ investment terms
  - Performance data visualization for investment strategies
  - Geographic allocation and sector positioning displays

**Files to Reference**:
- `public_site/models.py` - All page models and content types
- `public_site/wagtail_hooks.py` - Admin interface customizations
- `templates/public_site/` - All page templates

---

### 2. Form Processing & Security System

**What it does**: Handles contact forms, newsletter signups, and client onboarding with enterprise-grade spam protection.

**Security Layers** (Defense-in-Depth):
1. **Honeypot Fields** - Hidden fields that trap bots (2 per form)
2. **Cloudflare Turnstile** - Invisible CAPTCHA verification
3. **Timing Validation** - Rejects submissions < 10 seconds (bot) or > 1 hour (expired)
4. **Rate Limiting** - 3 submissions per hour per IP address
5. **Content Spam Detection** - Keyword filtering, URL counting, repetition analysis
6. **Domain Blocking** - Rejects known spam domains

**Form Types**:
- **Contact Form** (`AccessibleContactForm`):
  - Fields: name, email, company, subject, message
  - All security layers enabled
  - Email fallback if API unavailable

- **Newsletter Signup** (`AccessibleNewsletterForm`):
  - Fields: email, consent checkbox
  - HTMX-based for inline feedback
  - Single honeypot protection

- **Client Onboarding** (`OnboardingForm`):
  - **70+ fields** across 8 sections
  - Section 1: Personal information
  - Section 2: Co-client details (conditional)
  - Section 3: Contact preferences
  - Section 4: Risk assessment
  - Section 5: Values & investment goals
  - Section 6: Financial context
  - Section 7: Financial team & referrals
  - Section 8: Review & legal agreements
  - Alpine.js state management for multi-step flow
  - PO Box address detection and rejection (SEC compliance)
  - Conditional field validation based on user selections

**Accessibility**:
- WCAG 2.1 AA compliant
- Screen reader optimized
- Keyboard navigation support
- Clear error messages with ARIA labels

**Files to Reference**:
- `public_site/forms.py` - All form classes with validation
- `public_site/views.py` - Form submission handlers
- `templates/public_site/onboarding_page_comprehensive.html` - Multi-step onboarding UI

---

### 3. Frontend Architecture

**What it does**: Provides a modern, responsive, accessible design system with dark mode support.

**CSS Architecture**:
- **Tailwind CSS** (current, preferred):
  - Utility-first CSS framework
  - Custom Ethical Capital components: `.btn-ec-primary`, `.card-ec`, `.container-ec`
  - Brand colors: `ec-purple` (#581c87), `ec-teal` (#00ABB9)
  - Responsive breakpoints: sm (640px), md (768px), lg (1024px), xl (1280px), 2xl (1536px)
  - Dark mode support via `dark:` variants
  - Configuration in `tailwind.config.js`

- **Garden UI** (legacy, being phased out):
  - Comprehensive design system with 8 themes
  - CSS custom properties for colors, spacing, typography
  - Component classes: `.garden-panel`, `.garden-action`, `.garden-form`, `.garden-table`
  - Still functional during migration period

**Migration Success**:
- **84% reduction in `!important` declarations** (3,006 → 471)
- 56 CSS files tracked with quality metrics
- Emergency CSS files for critical fixes during transition

**Interactive Libraries**:
- **HTMX 1.9.11** - Server-driven interactivity without JavaScript
- **Alpine.js 3.14.1** - Lightweight reactive components
- **Chart.js** - Performance data visualization

**Template System**:
- Base template: `base_tailwind.html` (importance: 144.33)
- Modular blocks: title, meta_description, extra_css, content, extra_js
- Global includes: header, footer, navigation, analytics

**Typography**:
- Heading font: Bebas Neue
- Body font: Raleway
- Centralized in `static/css/typography-config.css`

**Files to Reference**:
- `static/css/dist/tailwind.min.css` - Compiled Tailwind CSS
- `static/css/garden-ui-theme.css` - Legacy Garden UI
- `tailwind.config.js` - Tailwind configuration
- `templates/public_site/base_tailwind.html` - Base template
- `css_baseline.json` - CSS quality metrics

---

### 4. Database Architecture

**What it does**: Provides flexible database support with intelligent fallback between multiple database systems.

**Multi-Database Support**:
1. **Kinsta PostgreSQL** (production primary)
   - Environment variable: `DB_URL`
   - Full-featured production database
   
2. **Ubicloud PostgreSQL** (import source)
   - Environment variable: `UBI_DATABASE_URL`
   - Connection testing with 5-second socket timeout
   - Used for importing existing content
   - Always available as 'ubicloud' alias

3. **SQLite** (development/fallback)
   - Environment variable: `USE_SQLITE=True`
   - Automatic fallback if PostgreSQL unavailable
   - Local development default

**Connection Features**:
- SSL/TLS certificate support
- Client certificate authentication
- Configurable SSL modes (disable, allow, prefer, require, verify-ca, verify-full)
- Automatic connection testing at startup
- Graceful degradation on failure

**Data Models**:
- Wagtail pages and content
- Performance metrics (monthly returns)
- Geographic allocations
- Sector positions
- Risk metrics
- Support tickets
- Media items
- User accounts

**Files to Reference**:
- `ethicic/settings.py` (lines 87-172) - Database configuration
- `runtime_init.sh` - Startup database selection logic
- `public_site/management/commands/safe_import_from_ubicloud.py` - Import command

---

### 5. External Service Integrations

**What it does**: Connects to third-party services for analytics, storage, caching, and bot protection.

**PostHog** (Analytics & Error Tracking):
- Automatic page view tracking
- Form submission events
- Search query tracking
- Frontend error capture (JavaScript errors, Promise rejections)
- Backend error capture via middleware
- Privacy controls: input masking, DNT respect, IP anonymization
- Session recording with data masking

**Cloudflare R2** (Media Storage):
- S3-compatible object storage
- Custom domain: images.ec1c.com
- Automatic image optimization
- AVIF and WebP format support
- Fallback to local filesystem

**Redis** (Caching & Sessions):
- Session storage (24-hour timeout)
- Query result caching (5-minute TTL)
- Rate limiting storage
- Automatic fallback to local memory cache

**Cloudflare Turnstile** (Bot Protection):
- Invisible CAPTCHA for forms
- Server-side validation
- Privacy-focused alternative to reCAPTCHA

**Google Tag Manager**:
- Marketing analytics
- Conversion tracking
- Custom event tracking

**Files to Reference**:
- `public_site/middleware.py` - PostHog error tracking
- `ethicic/settings.py` (lines 331-348) - PostHog configuration
- `templates/public_site/base_tailwind.html` - Analytics integration

---

### 6. Performance Calculation System

**What it does**: Calculates financial performance metrics for investment strategies from monthly return data.

**Calculations Performed**:
- **YTD Return** - Year-to-date performance
- **1-Year Return** - Trailing 12-month performance
- **3-Year Return** - 3-year annualized return
- **Since Inception Return** - Annualized return from strategy start date
- **Benchmark Comparison** - All metrics calculated for both strategy and benchmark
- **Difference Calculation** - Strategy vs. benchmark performance

**Data Structure**:
```python
monthly_returns = {
    2023: {
        1: {"strategy": "2.74%", "benchmark": "2.45%"},
        2: {"strategy": "1.89%", "benchmark": "2.12%"},
        # ... 12 months
    },
    2024: { ... }
}
```

**Key Functions**:
- `update_performance_from_monthly_data()` - Main orchestration function
- `calculate_ytd_return()` - Year-to-date calculation
- `calculate_one_year_return()` - Trailing 12 months
- `calculate_three_year_return()` - 3-year annualized
- `calculate_since_inception_return()` - Annualized since start
- `compound_returns()` - Cumulative return calculation: ∏(1 + r) - 1
- `parse_percentage()` - Converts "2.74%" → 0.0274
- `format_percentage()` - Converts 0.0274 → "2.74%"

**Files to Reference**:
- `public_site/utils/performance_calculator.py` - All calculation logic
- `ruff.toml` - Acknowledges legitimate complexity

---

### 7. Deployment Infrastructure

**What it does**: Provides Docker-based deployment with automated initialization and health monitoring.

**Container Startup Sequence** (`runtime_init.sh`):
1. **Database Selection** - Test and select available database
2. **Database Migrations** - `python manage.py migrate --noinput`
3. **Parallel Operations**:
   - Build Tailwind CSS: `npx postcss`
   - Build Garden UI: `python manage.py build_css`
   - Collect static files: `python manage.py collectstatic`
   - Import from Ubicloud: `python manage.py safe_import_from_ubicloud`
4. **Setup** - `python manage.py setup_homepage`
5. **Start Gunicorn** - 2 workers, 60-second timeout

**Docker Configuration**:
- Multi-stage build for optimization
- `uv` package installer (10-100x faster than pip)
- WhiteNoise for static file serving
- Health check endpoint: `/health/`
- Debug modes: `?debug=storage`, `?env=check`, `?list=media`

**Static File Serving**:
- WhiteNoise middleware with compression
- Cache-Control: max-age=3600 (1 hour)
- Cloudflare R2 for media files (optional)
- Local filesystem fallback

**Security Configuration**:
- HTTPS enforcement via `X-Forwarded-Proto`
- HSTS: 1 year (31,536,000 seconds)
- XSS filtering enabled
- Content type sniffing protection
- CSRF and session cookie security
- X-Frame-Options: DENY (clickjacking prevention)

**Environment Variables** (key configuration):
- `DEBUG` - Development mode toggle
- `SECRET_KEY` - Django secret (auto-generated if missing)
- `DB_URL` - Kinsta PostgreSQL connection
- `UBI_DATABASE_URL` - Ubicloud PostgreSQL for imports
- `USE_SQLITE` - Force SQLite mode
- `REDIS_URL` - Redis connection string
- `USE_R2` - Enable Cloudflare R2 media storage
- `POSTHOG_API_KEY` - PostHog analytics/error tracking
- `TURNSTILE_SECRET_KEY` - Cloudflare Turnstile bot protection
- `ALLOWED_HOSTS` - Comma-separated allowed domains

**Files to Reference**:
- `runtime_init.sh` - Container startup script
- `build.sh` - Build-time script
- `Dockerfile` - Multi-stage Docker build
- `ethicic/settings.py` - Django configuration

---

### 8. Management Commands

**What it does**: Provides 50+ Django management commands for deployment, content management, and maintenance.

**Key Commands**:

**Deployment**:
- `deploy` - Full deployment orchestration (migrations, CSS build, static collection)
- `setup_kinsta` - Kinsta-specific configuration
- `setup_homepage` - Initialize homepage with default content

**Content Management**:
- `safe_import_from_ubicloud` - Import pages, images, documents from Ubicloud
- `import_from_ubicloud` - Legacy import command
- `sync_cache` - Sync local cache with remote database

**CSS & Assets**:
- `build_css` - Build Garden UI CSS bundles
- `collectstatic` - Collect static files for production

**Database**:
- `migrate` - Run database migrations
- `makemigrations` - Create new migrations

**Development**:
- `runserver` - Development server
- `createsuperuser` - Create admin user
- `shell` - Django shell

**Files to Reference**:
- `public_site/management/commands/` - All management commands
- `public_site/management/commands/deploy.py` - Deployment orchestration
- `public_site/management/commands/setup_homepage.py` - Homepage initialization

---

### 9. Security Features

**What it does**: Implements enterprise-grade security across all layers of the application.

**Form Security** (covered in detail in section 2):
- Multi-layer spam protection
- Rate limiting (3 per hour per IP)
- Honeypot fields
- Cloudflare Turnstile
- Timing validation
- Content spam detection
- Domain blocking

**Application Security**:
- HTTPS enforcement in production
- HSTS with 1-year duration
- Secure cookie flags (HttpOnly, Secure, SameSite)
- CSRF protection on all forms
- XSS filtering
- Content type sniffing protection
- Clickjacking prevention (X-Frame-Options: DENY)

**Database Security**:
- SSL/TLS connections
- Client certificate authentication
- Connection string encryption
- SQL injection protection (Django ORM)

**Secrets Management**:
- Environment variable-based configuration
- No secrets in code or version control
- `.secrets.baseline` for secret scanning

**Compliance**:
- WCAG 2.1 AA accessibility compliance
- SEC compliance (PO Box rejection in onboarding)
- Privacy policy and terms of service
- GDPR-friendly (PostHog privacy controls)

**Files to Reference**:
- `public_site/forms.py` - Form security implementation
- `ethicic/settings.py` - Security middleware configuration
- `.secrets.baseline` - Secret scanning baseline

---

### 10. Documentation System

**What it does**: Provides comprehensive documentation for developers, designers, and content managers.

**Documentation Files** (20+ files):

**Architecture**:
- `docs/CSS_ARCHITECTURE_CURRENT.md` - CSS migration guide
- `docs/CSS_OVERVIEW.md` - CSS system overview
- `docs/DEVELOPMENT_WORKFLOW.md` - Development process
- `docs/POSTCSS_BUILD_PROCESS.md` - CSS build pipeline

**Design**:
- `docs/BRAND_COLORS.md` - Brand color system
- `docs/TYPOGRAPHY_USAGE.md` - Typography guidelines
- `garden-ui-handoff.md` - Garden UI design system handoff

**Operations**:
- `docs/POSTHOG_ERROR_TRACKING.md` - Error tracking setup
- `deployment-monitoring.md` - Deployment monitoring guide
- `IMPORT_AUDIT_REPORT.md` - Content import audit

**Quality**:
- `docs/ACCESSIBILITY_FIXES_2025-01-28.md` - Accessibility improvements
- `docs/CSS_TESTING.md` - CSS testing strategy
- `docs/CSS_LINTING_SETUP.md` - CSS linting configuration
- `security-report.md` - Security audit findings
- `ux-audit-notes.md` - UX audit notes

**Content**:
- `docs/about_text.md` - About page content
- `docs/homepage-cms-migration.md` - Homepage migration guide
- `docs/performance_system_readme.md` - Performance system documentation

**Developer Memory**:
- `CLAUDE.md` - Development memories and AI configuration
- `.claude/` - Claude AI project configuration

**Files to Reference**:
- `docs/` directory - All documentation files
- `CLAUDE.md` - Development context and decisions
- `README.md` - Setup and deployment guide

---

### 11. Testing Infrastructure

**What it does**: Provides testing utilities and scripts for quality assurance.

**Test Types**:
- Unit tests for models and utilities
- Integration tests for forms and views
- CSS quality monitoring
- Link checking
- Accessibility testing

**Test Scripts**:
- `run_tests_fast.py` - Fast test runner
- `count_tests.sh` - Test count utility
- `test_all_pages.sh` - Page accessibility testing
- `test_local.sh` - Local testing script
- `css_monitoring.py` - CSS quality tracking
- `enhanced_link_checker.py` - Comprehensive link validation

**Quality Metrics**:
- `css_baseline.json` - CSS quality baseline (56 files tracked)
- `css-specificity-audit.txt` - CSS specificity analysis
- `ethicic_wcag.csv` - WCAG compliance audit results

**Test Reports**:
- `BROKEN_LINKS_REPORT.md` - Link validation results
- `COMPREHENSIVE_LINK_CHECK_FINAL_REPORT.md` - Final link audit
- `WAGTAIL_IMAGE_UPLOAD_INVESTIGATION_REPORT.md` - Image upload debugging

**Files to Reference**:
- `tests/` directory - Test files
- `pytest.ini` - Pytest configuration
- `run_tests_fast.py` - Test runner
- `css_monitoring.py` - CSS quality monitoring

---

### 12. Additional Features

**URL Management**:
- SEO-friendly URLs
- Automatic sitemap generation (`/sitemap.xml`)
- Robots.txt configuration (`/robots.txt`)
- Carbon.txt for sustainability (`/carbon.txt`)
- LLMs.txt for AI crawlers (`/llms.txt`)

**Search**:
- Full-text search across pages
- Blog post search
- Encyclopedia search
- Search results page with highlighting

**Navigation**:
- Desktop navigation menu
- Mobile-responsive hamburger menu
- Breadcrumb navigation
- Footer navigation with multiple columns

**Media Management**:
- Automatic image optimization
- Multiple format support (AVIF, WebP, JPEG, PNG)
- Responsive images with srcset
- Document library for PDFs
- Media library with search and filtering

**Blog System**:
- Rich content with StreamField
- Categories and tags
- Related posts
- Reading time estimation
- Author profiles
- Featured images
- Social sharing

**Encyclopedia**:
- 100+ investment terms
- Difficulty levels (Beginner, Intermediate, Advanced)
- Categories (ESG, Basics, Ethics, Analysis)
- Related terms
- Examples and further reading

**Strategy Pages**:
- Performance metrics with charts
- Geographic allocation visualization
- Sector positioning (overweights/exclusions)
- Risk metrics display
- Holdings information
- Asset allocation breakdown

---

## What Worked Well

### 1. CSS Architecture Migration
The Tailwind CSS migration was highly successful, achieving an **84% reduction in `!important` declarations** (3,006 → 471). This dramatically reduced specificity conflicts and made the codebase more maintainable.

**Key Success Factors**:
- Utility-first approach reduced custom CSS
- Consistent design tokens
- Clear migration strategy with tracking
- Emergency CSS files for critical fixes during transition

### 2. Form Security System
The multi-layer security approach proved robust against spam and abuse. The defense-in-depth strategy with honeypots, Turnstile, timing validation, rate limiting, and content detection effectively blocked automated attacks while maintaining good user experience.

**Key Success Factors**:
- Multiple independent security layers
- Graceful degradation (email fallback)
- Accessibility maintained throughout
- Clear error messages for legitimate users

### 3. Database Fallback System
The intelligent multi-database system with automatic failover worked reliably across different environments. Connection testing at startup prevented deployment failures.

**Key Success Factors**:
- Automatic connection testing
- Clear fallback hierarchy
- SSL/TLS support
- Development-friendly (SQLite fallback)

### 4. External Service Integration
Clean integration patterns with graceful degradation ensured the site remained functional even when external services were unavailable.

**Key Success Factors**:
- Optional dependencies
- Fallback mechanisms
- Clear error handling
- Environment-based configuration

### 5. Documentation Discipline
Comprehensive documentation made the system maintainable and helped new developers understand the architecture quickly.

**Key Success Factors**:
- Architecture decision records
- Migration guides
- Inline code comments
- Developer memory (CLAUDE.md)

---

## What Could Be Improved

### 1. System Complexity
The system became complex with multiple databases, fallback mechanisms, and migration states. Future projects should consider simpler architectures unless complexity is truly necessary.

**Specific Issues**:
- Three database systems to maintain
- CSS migration in progress (dual systems)
- Multiple configuration paths
- Complex startup sequence

### 2. Deployment Process
The multi-stage deployment process with parallel operations could be simplified. Some operations could be moved to build-time rather than runtime.

**Specific Issues**:
- Long startup time (CSS builds, imports)
- Parallel operations increase complexity
- Multiple initialization scripts
- Environment-specific logic

### 3. Testing Coverage
Limited automated testing coverage meant more manual testing was required. More comprehensive unit and integration tests would improve confidence in changes.

**Specific Issues**:
- Few unit tests for models
- Limited integration tests
- No end-to-end tests
- Manual accessibility testing

### 4. Monolithic Architecture
The application could benefit from more modular architecture. Separating concerns (CMS, forms, calculations) into distinct services might improve maintainability.

**Specific Issues**:
- Single Django application
- Tightly coupled components
- Shared database for all features
- Difficult to scale individual components

### 5. CSS Migration Incomplete
While 84% complete, the CSS migration left some legacy Garden UI code that created maintenance burden.

**Specific Issues**:
- 31 of 56 CSS files still have issues
- 644 undefined CSS variables
- Emergency CSS files needed
- Dual system complexity

---

## Technology Stack Reference

### Backend
- **Django 5.1.5** - Web framework
- **Wagtail 7.0.1** - CMS
- **Python 3.11** - Programming language
- **Gunicorn 21.2.0** - WSGI server
- **psycopg2** - PostgreSQL adapter
- **redis-py** - Redis client

### Frontend
- **Tailwind CSS 4.1.11** - Utility-first CSS framework
- **HTMX 1.9.11** - Server-driven interactivity
- **Alpine.js 3.14.1** - Lightweight reactive framework
- **Chart.js** - Data visualization
- **PostCSS** - CSS processing

### Database
- **PostgreSQL** - Primary database (Kinsta, Ubicloud)
- **Redis 5.0.8** - Caching and sessions
- **SQLite** - Development fallback

### Deployment
- **Docker** - Containerization
- **Kinsta** - Hosting platform
- **WhiteNoise** - Static file serving
- **uv** - Fast Python package installer

### External Services
- **PostHog** - Analytics and error tracking
- **Cloudflare R2** - Object storage (S3-compatible)
- **Cloudflare Turnstile** - Bot protection
- **Google Tag Manager** - Marketing analytics

### Development Tools
- **Ruff** - Python linter and formatter
- **Stylelint** - CSS linter
- **Prettier** - Code formatter
- **ESLint** - JavaScript linter
- **pytest** - Testing framework

---

## For Future Projects

When building similar systems in the future, consider these lessons learned:

### 1. Reuse the Form Security Patterns
The multi-layer approach is battle-tested and effective. The combination of honeypots, Turnstile, timing validation, rate limiting, and content detection provides robust protection while maintaining accessibility.

**Recommended**: Copy `public_site/forms.py` as a starting point for any form-heavy application.

### 2. Learn from the CSS Migration
Starting with Tailwind CSS from day one would have avoided the migration complexity. The utility-first approach significantly reduced technical debt.

**Recommended**: Use Tailwind CSS from the start, avoid custom design systems unless absolutely necessary.

### 3. Simplify Database Strategy
Multiple database fallbacks added complexity that may not have been necessary. Consider a simpler approach with a single reliable database provider.

**Recommended**: Use a single managed PostgreSQL instance with good backups rather than multiple fallback systems.

### 4. Maintain Documentation Discipline
The comprehensive documentation was invaluable for maintenance and onboarding. Continue this practice in future projects.

**Recommended**: Document architecture decisions as they're made, not after the fact.

### 5. Invest in Testing Early
More automated testing would have caught issues earlier and made refactoring safer. Start with good test coverage from the beginning.

**Recommended**: Aim for 80%+ test coverage, especially for business logic and security-critical code.

### 6. Consider Modular Architecture
For larger projects, consider separating concerns into distinct services (microservices or modular monolith) rather than a single Django application.

**Recommended**: Evaluate whether the project would benefit from separation of CMS, forms, calculations, and other major systems.

### 7. Plan Migrations Carefully
The CSS migration was successful but took significant effort. Plan major migrations with clear milestones and tracking.

**Recommended**: Use metrics (like `css_baseline.json`) to track migration progress and prevent regression.

---

## Repository Status

- **Last Active Development**: 2025 (CSS migration completed)
- **Import Audit Status**: ✅ CLEAN - No critical import issues
- **Deployment Status**: ✅ APPROVED FOR DEPLOYMENT (as of audit)
- **CSS Migration**: 84% complete (471 `!important` declarations remaining)
- **Test Coverage**: Limited (needs improvement)
- **Documentation**: Comprehensive (20+ documentation files)
- **Current Purpose**: Feature inventory and historical reference only

---

## Important Notes

### Do Not Use This Repository for New Development

This repository is deprecated and should **not** be used as a starting point for new projects. It exists solely for reference and feature inventory purposes.

### Why Not Fork This?

While this codebase has many good features, it also has:
- Incomplete CSS migration (dual systems)
- Complex database fallback logic
- Limited test coverage
- Monolithic architecture
- Technical debt from multiple iterations

Starting fresh with lessons learned will be more efficient than trying to clean up this codebase.

### What You Can Take From This

Feel free to reference and adapt:
- Form security patterns (`public_site/forms.py`)
- Performance calculation logic (`public_site/utils/performance_calculator.py`)
- Tailwind configuration (`tailwind.config.js`)
- Documentation structure (`docs/`)
- Deployment patterns (`runtime_init.sh`, `Dockerfile`)

Just don't try to use the entire codebase as-is.

---

## Questions?

If you have questions about specific features or implementation details, refer to:
- The comprehensive onboarding guide in the repository notes
- Individual documentation files in `docs/`
- Code comments in key files
- `CLAUDE.md` for development context and decisions

---

**Last Updated**: October 25, 2025  
**Maintained By**: Historical reference only (no active maintainer)

# Deep Architectural Investigation: Ethical Capital Public Site
**Date**: January 24, 2025
**Investigation Scope**: Complete system architecture, patterns, and technical context

## System Overview

**Ethical Capital** (ethicic.com) is a sophisticated ESG (Environmental, Social, Governance) investment advisory firm built on a modern Django/Wagtail CMS architecture. This is not just a marketing website - it's a comprehensive financial services platform with advanced performance tracking, client onboarding, and content management capabilities.

## Core Business Context

- **Primary Service**: ESG-focused investment management with ethical screening
- **Target Clients**: Individual investors, RIAs (Registered Investment Advisors), institutional clients (endowments, foundations, pension funds)
- **Investment Strategies**: Growth, Income, and Diversification portfolios with activist divestment alignment (BDS, fossil fuels, weapons, tobacco, etc.)
- **Performance Tracking**: Real monthly portfolio returns vs benchmarks (MSCI ACWI TR)
- **Regulatory Environment**: SEC-regulated investment advisor with comprehensive compliance requirements

## Technical Architecture

### 1. Platform Foundation
- **Framework**: Django 4.x with Wagtail CMS 5.x
- **Architecture Pattern**: Monolithic with service-oriented components
- **Deployment**: Standalone mode (migrated from larger "Garden Platform")
- **Hosting**: Kinsta with PostgreSQL, Redis caching, WhiteNoise static files
- **Domain Migration**: Transitioned from ethicic.com to EC1C.com (evident in URL redirects)

### 2. Database Architecture
```
Multi-Database Strategy:
├── Primary: Ethicic Public PostgreSQL (Kinsta)
├── Secondary: Ubicloud PostgreSQL (legacy import)
├── Development: SQLite fallback
└── Caching: Redis for sessions and query caching
```

**Key Features**:
- Connection pooling with 600s max age
- SSL-required connections in production
- Graceful fallback strategies with connection testing
- Schema validation for safe data migration

### 3. Content Management System (Wagtail)

**Page Types Hierarchy**:
```
HomePage (/)
├── AboutPage (/about/)
├── StrategyPage (/strategies/*)
│   ├── Growth Strategy
│   ├── Income Strategy
│   └── Diversification Strategy
├── BlogIndexPage (/blog/)
│   └── BlogPost (/blog/[slug]/)
├── MediaPage (/media/)
├── FAQIndexPage (/faq/)
│   └── FAQArticle (/faq/[slug]/)
├── ProcessPage (/process/)
├── ContactFormPage (/contact/)
├── OnboardingPage (/onboarding/)
├── PricingPage (/pricing/)
└── LegalPage (/disclosures/)
```

**Advanced Features**:
- StreamField for flexible rich content
- Multi-format image optimization (AVIF, WebP, JPEG)
- 20MB file upload limit, 128MP image processing
- Custom user forms (disabled avatar uploads for Kinsta compatibility)

### 4. Performance Data Management

**Financial Performance System**:
- Monthly return data stored as JSON with strategy/benchmark pairs
- Automated calculation of YTD, 1-year, 3-year, and since-inception returns
- Compound return calculations with annualization
- Risk-adjusted performance metrics
- Benchmark comparison (MSCI ACWI TR)

**Data Format Example**:
```json
{
  "2025": {
    "Jan": {"strategy": "2.74%", "benchmark": "3.28%"},
    "Feb": {"strategy": "2.49%", "benchmark": "-0.35%"}
  }
}
```

### 5. Form System & Client Onboarding

**Accessibility-First Design** (WCAG 2.1 AA compliant):
- Crispy Forms with Bootstrap 4 styling
- ARIA attributes and semantic HTML
- Comprehensive help text and error messages

**Advanced Spam Protection**:
- Cloudflare Turnstile integration
- Multiple honeypot fields
- Rate limiting with Redis
- Form timing validation (10s minimum, 1hr maximum)
- Content spam detection with keyword analysis
- URL count limits and repetition detection

**Comprehensive Client Onboarding** (70+ fields):
- Personal information (including pronouns, preferred names)
- Co-client support for joint accounts
- 7-question risk tolerance assessment
- Ethical investment preferences aligned with divestment movements
- Financial context and experience evaluation
- Professional team coordination

### 6. Security Implementation

**Production Security Configuration**:
- XSS filtering and content type sniffing prevention
- HSTS with subdomains (1-year expiry)
- Secure cookies for HTTPS
- CSRF protection with secure cookies
- X-Frame-Options for clickjacking prevention
- Proxy-aware SSL handling for load balancers

**API Security**:
- Form encryption for sensitive submissions
- Backend API key authentication
- Turnstile bot protection
- IP-based rate limiting

### 7. CSS Architecture & Design System

**Garden UI Design System**:
- BEM-based CSS architecture with 64+ component files
- PostCSS build pipeline combining files into optimized bundles
- CSS variables for consistent theming (never hardcoded colors)
- Automated linting with Stylelint (BEM pattern enforcement)
- Pre-commit hooks preventing CSS conflicts
- Build commands: `npm run build:css:dev` and `npm run build:css:prod`

**Performance Optimization**:
- WhiteNoise for static file serving with compression
- Manifest storage for cache busting
- CSS file combination: 64 files → 1 optimized bundle
- ~50% reduction in HTTP requests

### 8. Integration Architecture

**External Services**:
- **Cloudflare Turnstile**: Bot protection and form validation
- **Email Integration**: SMTP with development console fallback
- **Redis Caching**: Session management and query optimization
- **Main Platform API**: Integration with larger "Garden Platform"

**API Endpoints** (50+ routes):
- Form submission endpoints (`/contact/submit/`, `/onboarding/submit/`)
- JSON APIs for AJAX functionality
- Search functionality with live endpoints
- Media items API for infinite scroll
- Theme preference management
- HTMX polling for real-time updates

### 9. Operational Management

**Management Commands** (50+ commands):
- **Content Migration**: `import_from_ubicloud`, `safe_import_from_ubicloud`
- **Performance Data**: `import_performance_csv`, `show_performance`
- **Site Setup**: `setup_standalone`, `setup_kinsta`, `setup_wagtail_pages`
- **Data Maintenance**: `fix_database`, `sync_cache`, `update_media_dates`
- **Deployment**: `deploy`, `check_database_schema`

**Logging Configuration**:
- Separate loggers for Django core, requests, and application
- Console and file logging with structured formatting
- DEBUG level for application code, INFO for Django core

### 10. Testing Philosophy

**Comprehensive Test Coverage**:
- Unit tests for models, forms, views, and utilities
- Integration tests for form workflows
- Performance calculation test suites
- Accessibility validation tests
- API endpoint testing
- 90%+ coverage goals evident from test structure

**Test Categories**:
- Form validation (spam protection, accessibility)
- Financial calculations (compound returns, annualization)
- Content management (Wagtail page creation, media handling)
- Security features (rate limiting, input validation)

## Code Quality & Development Practices

### 1. Code Organization
- **Single App Architecture**: All functionality in `public_site` app
- **Clean Separation**: Models, forms, views, utilities properly separated
- **Template Inheritance**: Consistent base templates with component reuse
- **URL Patterns**: RESTful routing with proper namespacing

### 2. Security-First Development
- Environment variable configuration for all secrets
- Proper database connection handling with SSL
- Input validation and sanitization throughout
- CSRF protection on all forms
- SQL injection prevention with Django ORM

### 3. Performance Optimization
- Database query optimization with select_related/prefetch_related
- Redis caching for expensive operations
- Static file optimization with compression
- Image processing with multiple format support
- Connection pooling for database efficiency

### 4. Accessibility & UX
- WCAG 2.1 AA compliance throughout
- Semantic HTML with proper ARIA attributes
- Keyboard navigation support
- Screen reader optimization
- Progressive enhancement patterns

## Migration & Deployment Story

**Infrastructure Evolution**:
1. **Original Platform**: Part of larger "Garden Platform" ecosystem
2. **Ubicloud Phase**: Intermediate hosting with PostgreSQL
3. **Kinsta Deployment**: Current standalone deployment with optimized stack
4. **Domain Transition**: ethicic.com → EC1C.com (SEO redirects maintained)

**Migration Tooling**:
- Safe import commands with schema validation
- Dry-run capabilities for testing
- Multi-database connection management
- Content preservation with relationship integrity

## Business Intelligence & Analytics

**Performance Metrics**:
- Real-time portfolio performance tracking
- Monthly return calculations with compound interest
- Benchmark comparison analysis
- Risk-adjusted return metrics
- Historical performance data since 2021

**Client Analytics**:
- Comprehensive risk profiling questionnaire
- Ethical investment preference mapping
- Financial capacity assessment
- Professional network coordination

## Remarkable Technical Insights

### 1. Financial Services Grade Architecture
This isn't a typical CMS - it's built for SEC-regulated investment management with real money and regulatory compliance requirements.

### 2. Sophisticated Form Engineering
The onboarding form system rivals enterprise SaaS applications with 70+ fields, conditional logic, and comprehensive validation.

### 3. Advanced Spam Protection
Multi-layered bot detection that goes far beyond typical website forms, including behavioral analysis and timing validation.

### 4. Performance-First CSS Architecture
The Garden UI system with PostCSS build pipeline shows enterprise-grade front-end engineering.

### 5. Accessibility Excellence
True WCAG 2.1 AA compliance, not just checkboxes - built for users with disabilities from the ground up.

### 6. Multi-Database Mastery
Sophisticated database architecture with connection testing, fallbacks, and safe migration tooling.

### 7. Content Management Sophistication
Wagtail implementation goes beyond basic CMS - StreamFields, image optimization, and complex page hierarchies.

## Conclusion

**Ethical Capital's public site represents a sophisticated financial technology platform disguised as a content website.** The technical architecture supports:

- Real investment portfolio management
- SEC regulatory compliance
- Comprehensive client onboarding
- Performance reporting and analytics
- Multi-stakeholder content management
- Enterprise-grade security and accessibility

The codebase demonstrates **senior-level engineering practices** across the entire stack, with particular strength in:
- Database architecture and performance optimization
- Security-first development practices
- Accessibility and inclusive design
- Modern CSS architecture and build systems
- Comprehensive testing and quality assurance

This is a **production-grade financial services platform** that could serve as a reference implementation for Django/Wagtail applications in regulated industries.

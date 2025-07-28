## Development Memories
- if you update the garden views in the web container, implement the same change in the public container.
- dont use hardcoded styles in css -- use our garden ui variables so that we dont have issues applying styles in the future
- **NEVER use hardcoded colors in CSS** - ALL colors must use Garden UI theme variables for centralized theme management
- **Prefer @core/widgets/ components** wherever possible for consistent UI patterns and behavior
- dont make up things on our public website. DO NOT
- when i ask you to help me edit content, make ONLY the edits i explicitly suggest. Do not take initiative.
- **dont fix things with bandaids. Create clean codes**
- dont work around issues. solve them
- always use garden ui componoents and widgets to impplement new pages
- use garden ui, not bootstrap
- always use garden ui
- i turned off the cdn for now
- NEVER just remove a file thats causing issues. THat's lazy bullshit and we dont do it around here#
- we are often making multiple edits in parallel -- if you come across an issue that might be due to that, consider this before you make any actions
- sleep 120 after you push -- it takes time to rebuild

## CSS Architecture (RATIONAL SYSTEM - 2025)
- **CONSOLIDATED**: 84% !important reduction achieved - 83 files → 58 files, 3,006 → 471 !important declarations
- **NEW ARCHITECTURE**: responsive-layout-system.css, header-layout-layers.css, mobile-navigation-layers.css + existing clean files
- **RULES**: Use Garden UI variables only, CSS Layers architecture, no !important wars
- **DOCUMENTATION**: See `docs/CSS_OVERVIEW.md` for quick start and `docs/CSS_ARCHITECTURE_CURRENT.md` for complete reference

## CSS Architecture Protection Rules (CRITICAL - DO NOT VIOLATE)
- **NEVER create new "*-fix.css" files** - Always enhance existing clean files or create proper layered architecture
- **NEVER add !important declarations** - Use CSS Layers (@layer) for cascade management instead
- **NEVER create competing CSS files** - One file per responsibility, consolidate conflicts immediately
- **ALWAYS use existing clean files** - responsive-layout-system.css, header-layout-layers.css, mobile-navigation-layers.css
- **BEFORE creating ANY CSS file** - Check if functionality exists in current clean architecture
- **CSS LAYERS ONLY** - All new CSS must use @layer (layout, components, themes, utilities) architecture
- **NO HARDCODED VALUES** - Use Garden UI variables: --color-*, --space-*, --font-*, --radius-* only
- **FIX ROOT CAUSES** - Never bandaid with specificity wars, always address architectural issues properly

## System Architecture Context (Investigation - Jan 2025)
- **Business Domain**: Ethical Capital - SEC-regulated ESG investment advisory firm managing real portfolios
- **Technical Stack**: Django 4.x + Wagtail 5.x CMS with PostgreSQL, Redis caching, Kinsta hosting
- **Architecture**: Monolithic with service-oriented components, standalone deployment (migrated from "Garden Platform")
- **Key Models**: StrategyPage (with performance calculations), BlogPost, OnboardingForm, MediaItem
- **Performance Data**: Monthly investment returns stored as JSON, compound calculations in `public_site/utils/performance_calculator.py`
- **Multi-Database**: Primary (Kinsta PostgreSQL), Secondary (Ubicloud legacy), Fallback (SQLite)
- **Management Commands**: 50+ commands for content migration, performance import, site setup - see `management/commands/`
- **Security**: Enterprise-grade with Cloudflare Turnstile, multi-layer spam protection, WCAG 2.1 AA compliance
- **Forms**: Sophisticated client onboarding (70+ fields), comprehensive validation, accessibility-first design
- **API Endpoints**: 50+ routes for form submissions, AJAX functionality, search, media APIs
- **Investigation Report**: See `.claude/docs/investigation-2025-01-24.md` for comprehensive architecture analysis
- **Current Documentation**: See `docs/README.md` for complete documentation index
- **KEEP DOCS CURRENT**: Always update documentation when making architectural changes, new features, or process modifications
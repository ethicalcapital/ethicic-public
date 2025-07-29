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

## CSS Architecture Migration (2025 - CURRENT)
- **MIGRATION TO TAILWIND**: Moving away from Garden UI system to pure Tailwind CSS for maintainability
- **CONSOLIDATED**: 84% !important reduction achieved - 83 files → 58 files, 3,006 → 471 !important declarations
- **TAILWIND FIRST**: All new templates use Tailwind utilities and @apply directives
- **LEGACY GARDEN UI**: Still present in some templates, being gradually migrated
- **DOCUMENTATION**: See `docs/CSS_OVERVIEW.md` for quick start and `docs/CSS_ARCHITECTURE_CURRENT.md` for complete reference

## CSS Architecture Rules (CURRENT MIGRATION STRATEGY)
- **PREFER TAILWIND**: Use Tailwind utilities over Garden UI variables for new development
- **NO HARDCODED COLORS**: Use Tailwind color system (slate, purple, teal) for brand consistency
- **MIGRATION PRIORITY**: Templates extending base_tailwind.html → pure Tailwind first
- **LEGACY SUPPORT**: Garden UI still functional for existing components during transition
- **CSS LAYERS**: Use @layer for complex styling when Tailwind utilities aren't sufficient
- **NO !IMPORTANT**: Avoid specificity wars - use Tailwind's specificity hierarchy
- **RESPONSIVE FIRST**: Use Tailwind's mobile-first responsive utilities (sm:, md:, lg:)
- **DARK MODE**: Use Tailwind's dark: variants for theme switching

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

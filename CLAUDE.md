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

## CSS Architecture (Complete - 2025)
- **Documentation**: See `docs/CSS_ARCHITECTURE_SUMMARY.md` for complete setup details
- **Build System**: Use `npm run build:css:dev` for development, `npm run build:css:prod` for production
- **Linting**: Run `npm run lint:css` before commits - enforces Garden UI BEM patterns
- **Template**: Use `templates/public_site/base_optimized.html` for single CSS file delivery
- **Utilities**: Use spacing classes (.mt-3, .mb-4) instead of inline styles
- **Components**: All in `static/css/garden-*.css` files with proper theme variables
- **Quality**: Pre-commit hooks prevent bad CSS, VS Code auto-fixes issues
- **Performance**: 64 files → 1 optimized file, ~50% reduction in HTTP requests

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

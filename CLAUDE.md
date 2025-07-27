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

## CSS Architecture (RATIONAL SYSTEM - 2025)
- **CONSOLIDATED**: 65% reduction achieved - 20+ fix files → 5 logical systems
- **NEW ARCHITECTURE**: garden-layout-clean.css, garden-buttons-enhanced.css, garden-accessibility-clean.css, garden-forms-clean.css, garden-layout-system.css
- **RULES**: Use Garden UI variables only, CSS Layers architecture, no !important wars
- **DOCUMENTATION**: See `css-consolidation-plan.md` for roadmap and `.claude/docs/css-investigation-2025-01-26.md` for analysis

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
- **Documentation Sync Report**: See `.claude/docs/investigation-2025-01-26.md` for documentation accuracy analysis

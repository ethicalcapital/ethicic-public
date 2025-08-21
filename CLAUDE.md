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

---

# AI Development Team Configuration
*Generated: 2025-07-30 | Updated by: team-configurator*

## Project Technology Stack Analysis

**Primary Framework Stack:**
- **Backend**: Django 5.1.5 + Wagtail 7.0.1 CMS
- **Frontend**: CSS Migration (Garden UI → Tailwind CSS 4.1.11)
- **Database**: PostgreSQL (Multi-database: Kinsta Primary, Ubicloud Secondary, SQLite Fallback)
- **Caching**: Redis 5.0.8 with django-redis
- **Security**: Cloudflare Turnstile, WCAG 2.1 AA compliance
- **Hosting**: Kinsta with Gunicorn 21.2.0
- **CSS Build**: PostCSS with custom build pipeline
- **Package Management**: uv (Python), npm (Node.js)
- **Code Quality**: Ruff, Black, isort, Stylelint, Prettier
- **Testing**: pytest, pytest-django, pytest-cov

**Key Business Domain:**
- SEC-regulated ESG investment advisory firm
- Real portfolio management with performance calculations
- Client onboarding (70+ field forms)
- Investment strategy pages with JSON performance data
- Enterprise-grade security and compliance requirements

## Optimal AI Agent Assignments

### 1. Django Backend Development
- **Primary**: `django-backend-expert` - Comprehensive Django/Wagtail development
- **Secondary**: `django-orm-expert` - Complex model relationships and performance
- **API**: `django-api-developer` - REST endpoints, AJAX functionality
- **Tasks**: Model design, view implementation, management commands, Wagtail admin customization

### 2. Frontend & CSS Architecture  
- **Primary**: `tailwind-frontend-expert` - Leading the Garden UI → Tailwind migration
- **Tasks**: Responsive components, CSS consolidation, design system migration, accessibility compliance

### 3. Performance & Optimization
- **Primary**: `performance-optimizer` - Database queries, caching, load optimization
- **Tasks**: Investment calculation performance, multi-database optimization, Redis caching strategies

### 4. Security & Compliance
- **Primary**: `security-auditor` - Enterprise security, SEC compliance, WCAG standards
- **Tasks**: Form validation security, data protection, vulnerability assessments, accessibility audits

### 5. Code Quality & Review
- **Primary**: `code-quality-analyst` - Comprehensive code review and quality assessment
- **Secondary**: `code-reviewer` - Focused code review for specific components
- **Enforcer**: `excellence-enforcer` - Rigorous quality evaluation and accountability

### 6. Project Management & Strategy
- **Orchestrator**: `tech-lead-orchestrator` - Strategic planning, architecture decisions
- **Coordinator**: `four-track-orchestrator` - Multi-stream parallel development coordination
- **Curator**: `strategic-questions-curator` - Strategic direction and milestone assessment

### 7. Deployment & Infrastructure
- **Monitor**: `kinsta-deployment-monitor` - Kinsta-specific deployment monitoring
- **Sentinel**: `deployment-sentinel` - General deployment monitoring and wait operations

### 8. Documentation & Analysis
- **Specialist**: `documentation-specialist` - Technical documentation, API docs, guides
- **Archaeologist**: `code-archaeologist` - Legacy codebase exploration and onboarding
- **Analyst**: `project-analyst` - Technology stack analysis and architecture discovery

### 9. Task Routing & Coordination
- **Concierge**: `task-concierge` - Intelligent task routing to appropriate specialists
- **Configurator**: `team-configurator` - AI team setup and configuration management

## Common Workflow Patterns

### Django Model Development
1. `django-backend-expert` → Model design and implementation
2. `django-orm-expert` → Performance optimization and relationships
3. `security-auditor` → Security validation
4. `code-quality-analyst` → Code review
5. `excellence-enforcer` → Final quality assessment

### Frontend Migration (Garden UI → Tailwind)
1. `tailwind-frontend-expert` → Component migration and responsive design
2. `code-quality-analyst` → CSS quality and maintainability review
3. `performance-optimizer` → Bundle size and load performance
4. `security-auditor` → Frontend security validation

### Investment Performance System
1. `django-backend-expert` → Model and calculation logic
2. `performance-optimizer` → Performance calculation optimization
3. `security-auditor` → Financial data security compliance
4. `documentation-specialist` → Algorithm and API documentation

### Client Onboarding Forms
1. `django-backend-expert` → Form backend logic and validation
2. `tailwind-frontend-expert` → Accessible form UI components
3. `security-auditor` → Input validation and data protection
4. `code-quality-analyst` → Form logic review

### Management Commands & Data Migration
1. `django-backend-expert` → Command implementation
2. `performance-optimizer` → Large dataset processing optimization
3. `security-auditor` → Data integrity and security validation

### Enterprise Deployment
1. `kinsta-deployment-monitor` → Kinsta-specific deployment management
2. `deployment-sentinel` → Process monitoring and coordination
3. `security-auditor` → Production security validation
4. `performance-optimizer` → Production performance monitoring

## Agent Collaboration Rules

### Quality Pipeline
- All production code MUST pass through `code-quality-analyst` OR `code-reviewer`
- Critical systems (finance, security, forms) MUST be reviewed by `excellence-enforcer`
- Security-sensitive changes MUST be validated by `security-auditor`

### CSS Migration Priority
- New development: Use `tailwind-frontend-expert` exclusively
- Legacy updates: Coordinate between `tailwind-frontend-expert` and existing Garden UI
- Performance impact: Include `performance-optimizer` for large CSS changes

### Django Best Practices
- Complex models: Engage `django-orm-expert` for relationship design
- API development: Use `django-api-developer` for endpoints
- Admin customization: Primary responsibility of `django-backend-expert`

### Documentation Requirements
- Architecture changes: `documentation-specialist` must update relevant docs
- New features: Include usage examples and API documentation
- Security features: Document compliance and security considerations

## Task Routing Examples

**"Fix performance issues in investment calculations"**
→ `performance-optimizer` (primary) + `django-backend-expert` (implementation) + `django-orm-expert` (database optimization)

**"Migrate contact form from Garden UI to Tailwind"**
→ `tailwind-frontend-expert` (primary) + `security-auditor` (form security) + `code-quality-analyst` (review)

**"Add new API endpoint for client data"**
→ `django-api-developer` (primary) + `security-auditor` (API security) + `documentation-specialist` (API docs)

**"Optimize database queries for strategy pages"**
→ `django-orm-expert` (primary) + `performance-optimizer` (monitoring) + `code-quality-analyst` (review)

**"Deploy new feature to Kinsta production"**
→ `kinsta-deployment-monitor` (primary) + `deployment-sentinel` (coordination) + `security-auditor` (security validation)

## Coverage Assessment

### ✅ Well Covered Areas
- Django/Wagtail backend development
- Tailwind CSS frontend migration
- Security and compliance validation
- Code quality and review processes
- Performance optimization
- Deployment monitoring
- Project management and coordination

### ⚠️ Potential Gaps
- **Financial Domain Expertise**: Consider specialized financial calculation validation
- **Wagtail CMS Specialist**: Current Django experts cover this, but deeper CMS expertise could be valuable
- **Accessibility Specialist**: Currently covered by security-auditor, but dedicated WCAG expert could enhance compliance
- **Load Testing**: Performance optimizer covers optimization, but dedicated load testing might be needed

### 🔧 Recommendations
1. **Financial Calculations**: Add financial domain validation to `security-auditor` workflows
2. **CMS Content Strategy**: Leverage `documentation-specialist` for content management workflows
3. **Accessibility Testing**: Enhance `security-auditor` with specific WCAG 2.1 AA testing protocols
4. **Performance Monitoring**: Integrate continuous performance monitoring into deployment workflows

This configuration provides comprehensive coverage for your Django/Wagtail project with proper specialization, quality controls, and coordination mechanisms tailored to your SEC-regulated investment advisory business requirements.

# Ethical Capital Documentation

This directory contains comprehensive documentation for the Ethical Capital website and platform.

## 📚 Documentation Index

### CSS Architecture & Build System
- **[CSS_OVERVIEW.md](CSS_OVERVIEW.md)** - Quick start guide for CSS changes (START HERE)
- **[CSS_ARCHITECTURE_CURRENT.md](CSS_ARCHITECTURE_CURRENT.md)** - Complete technical reference (2025 Rational Architecture)
- **[POSTCSS_BUILD_PROCESS.md](POSTCSS_BUILD_PROCESS.md)** - Build system documentation
- **[CSS_LINTING_SETUP.md](CSS_LINTING_SETUP.md)** - Linting and quality control

### Development & Maintenance
- **[CSS_MAINTENANCE_GUIDE.md](CSS_MAINTENANCE_GUIDE.md)** - Complete CSS conflict prevention system
- **[DEVELOPMENT_WORKFLOW.md](DEVELOPMENT_WORKFLOW.md)** - Developer workflow and tools
- **[FRONTEND_RENAISSANCE.md](FRONTEND_RENAISSANCE.md)** - Frontend architecture and design patterns

### Testing & Quality
- **[CSS_TESTING.md](CSS_TESTING.md)** - CSS testing infrastructure and best practices
- **[LINTING.md](LINTING.md)** - Code linting and quality control

### Migration Documentation
- **[inline-style-migration.md](inline-style-migration.md)** - Inline style migration guide
- **[archive/css-legacy-2025-01/](archive/css-legacy-2025-01/)** - Archived CSS documentation (pre-consolidation)
- **[archive/deployment-legacy-2025/](archive/deployment-legacy-2025/)** - Archived deployment documentation (outdated)

### Deployment & Infrastructure
- **[KINSTA_DEPLOYMENT_CHECKLIST.md](KINSTA_DEPLOYMENT_CHECKLIST.md)** - Kinsta deployment checklist
- **[KINSTA_DEPLOYMENT_FINAL_STEPS.md](KINSTA_DEPLOYMENT_FINAL_STEPS.md)** - Final deployment steps

### Architecture & Systems
- **[MONITORING_SYSTEMS.md](MONITORING_SYSTEMS.md)** - Automated monitoring and CI/CD systems
- **[performance_system_readme.md](performance_system_readme.md)** - Performance system documentation

### Content & Features
- **[homepage-cms-migration.md](homepage-cms-migration.md)** - Homepage CMS migration
- **[onboarding_form.md](onboarding_form.md)** - Onboarding form documentation
- **[about_text.md](about_text.md)** - About page content
- **[pri_ddq.md](pri_ddq.md)** - PRI DDQ documentation

### Reference Files
- **[errorlogs.md](errorlogs.md)** - Error logging and debugging
- **[performance_calculation.md](performance_calculation.md)** - Performance calculation methods
- **[archive/](archive/)** - Historical documentation and audits

## 🎯 Quick Reference

### CSS Development
```bash
npm run build:css:dev     # Development build
npm run build:css:prod    # Production build
npm run lint:css          # Lint CSS files
npm run lint:css:fix      # Auto-fix linting issues
npm run quality          # Lint + production build
```

### Common Tasks
- **Before CSS changes**: Always run `npm run lint:css`
- **Adding new variables**: Add to `static/css/garden-ui-theme.css`
- **Template updates**: Use Garden UI classes (`garden-*`) and utility classes (`.mt-3`, `.mb-4`)
- **Building CSS**: Use `npm run build:css:dev` for development
- **Optimized template**: Use `templates/public_site/base_optimized.html`

## 🔧 System Status

### Current Metrics (July 27, 2025)
- ✅ **Rational CSS Architecture** - 65% consolidation complete
- ✅ **20+ fix files → 5 logical systems** consolidated
- ✅ **Garden UI variables** throughout (no hardcoded colors)
- ✅ **CSS Layers architecture** for proper cascade
- ✅ **WCAG AA compliance** built-in
- ✅ **Performance optimized** with fewer HTTP requests

### Protection Against
- CSS specificity wars (eliminated !important battles)
- Scattered fix files (consolidated into logical systems)
- Hardcoded values (Garden UI variables enforced)
- Accessibility issues (WCAG AA built-in)
- Code quality regressions (pre-commit validation)

## 📖 Getting Started

1. **Read the CSS Overview** first: [CSS_OVERVIEW.md](CSS_OVERVIEW.md)
2. **Install dependencies**: `npm install`
3. **Build CSS**: `npm run build:css:dev`
4. **Run linting**: `npm run lint:css`

## 🆘 Emergency Procedures

If CSS builds or linting fail:
1. Check recent commits: `git log --oneline -10`
2. Run linting: `npm run lint:css`
3. Auto-fix issues: `npm run lint:css:fix`
4. Check build logs: `npm run build:css:dev`
5. Use workflow helper: `./lint-workflow.sh`

---

All documentation is kept up-to-date and reflects the current state of the system. For system-specific issues, consult the relevant guide above.

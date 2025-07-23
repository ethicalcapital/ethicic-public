# Ethical Capital Documentation

This directory contains comprehensive documentation for the Ethical Capital website and platform.

## 📚 Documentation Index

### CSS Architecture & Build System
- **[CSS_ARCHITECTURE_SUMMARY.md](CSS_ARCHITECTURE_SUMMARY.md)** - Complete overview of CSS architecture
- **[CSS_ARCHITECTURE.md](CSS_ARCHITECTURE.md)** - CSS architecture, theme system, and variables
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
- **[css-override-elimination-plan.md](css-override-elimination-plan.md)** - Plan for removing override files
- **[css-integration-final-summary.md](css-integration-final-summary.md)** - Override elimination summary
- **[inline-style-migration.md](inline-style-migration.md)** - Inline style migration guide
- **[css-testing-checklist.md](css-testing-checklist.md)** - CSS testing procedures

### Deployment & Infrastructure
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Main deployment instructions
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
- **[garden-ui-override-mapping.md](garden-ui-override-mapping.md)** - Override file mapping
- **[override-files-to-remove.md](override-files-to-remove.md)** - Files to be removed
- **[wcag_contrast_audit_report.md](wcag_contrast_audit_report.md)** - Accessibility audit
- **[errorlogs.md](errorlogs.md)** - Error logging and debugging
- **[performance_calculation.md](performance_calculation.md)** - Performance calculation methods

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

### Current Metrics
- ✅ **Complete CSS architecture** with build system
- ✅ **64 CSS files** combined into 1 optimized file
- ✅ **~50% reduction** in HTTP requests
- ✅ **CSS linting** enforces Garden UI BEM patterns
- ✅ **Git hooks** prevent bad CSS commits
- ✅ **PostCSS build process** with dev/prod modes

### Protection Against
- CSS override technical debt (eliminated 22 override files)
- Inline style pollution (migrated to utility classes)
- Naming inconsistencies (enforced BEM patterns)
- Performance regressions (optimized builds)
- Code quality issues (pre-commit validation)

## 📖 Getting Started

1. **Read the CSS Architecture Summary** first: [CSS_ARCHITECTURE_SUMMARY.md](CSS_ARCHITECTURE_SUMMARY.md)
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

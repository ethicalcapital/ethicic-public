# Ethical Capital Documentation

This directory contains comprehensive documentation for the Ethical Capital website and platform.

## 📚 Documentation Index

### Development & Maintenance
- **[CSS_MAINTENANCE_GUIDE.md](CSS_MAINTENANCE_GUIDE.md)** - Complete CSS conflict prevention system
- **[FRONTEND_RENAISSANCE.md](FRONTEND_RENAISSANCE.md)** - Frontend architecture and design patterns

### Testing & Quality
- **[CSS_TESTING.md](CSS_TESTING.md)** - CSS testing infrastructure and best practices
- **[DEVELOPMENT_WORKFLOW.md](DEVELOPMENT_WORKFLOW.md)** - Developer workflow and tools

### Architecture & Systems
- **[CSS_ARCHITECTURE.md](CSS_ARCHITECTURE.md)** - CSS architecture, theme system, and variables
- **[MONITORING_SYSTEMS.md](MONITORING_SYSTEMS.md)** - Automated monitoring and CI/CD systems

## 🎯 Quick Reference

### CSS Development
```bash
make css-check      # Quick conflict check
make css-test       # Run full CSS test suite
make css-baseline   # Create new baseline
make css-report     # Generate detailed report
```

### Common Tasks
- **Before CSS changes**: Always run `make css-check`
- **Adding new variables**: Add to `static/css/garden-ui-theme.css`
- **Template updates**: Use Garden UI classes (`garden-*`)
- **Debugging conflicts**: Check `docs/CSS_MAINTENANCE_GUIDE.md`

## 🔧 System Status

### Current Metrics
- ✅ **0 undefined CSS variables** across all files
- ✅ **300+ theme variables** properly defined
- ✅ **44 CSS files** monitored and conflict-free
- ✅ **10/10 CSS tests** passing
- ✅ **Git hooks** preventing conflicts
- ✅ **CI/CD pipeline** ensuring quality

### Protection Against
- CSS variable conflicts (auto-detected and blocked)
- Template inconsistencies (Garden UI validation)
- Performance regressions (file size monitoring)
- Accidental breakage (pre-commit validation)
- Future conflicts (baseline tracking)

## 📖 Getting Started

1. **Read the CSS Maintenance Guide** first: [CSS_MAINTENANCE_GUIDE.md](CSS_MAINTENANCE_GUIDE.md)
2. **Install git hooks**: `make install-hooks`
3. **Check current status**: `make css-check`
4. **Run tests**: `make css-test`

## 🆘 Emergency Procedures

If CSS tests start failing:
1. Check recent commits: `git log --oneline -10`
2. Run diagnostic: `make css-report`
3. Fix undefined variables: Add to `garden-ui-theme.css`
4. Nuclear option: `make css-baseline` (creates new baseline)

---

All documentation is kept up-to-date and reflects the current state of the system. For system-specific issues, consult the relevant guide above.

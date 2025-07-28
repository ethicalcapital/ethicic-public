# Codebase Cruft Cleanup Plan

## Immediate Safe Deletions

### Backup Files (3 files)
```bash
rm tests/unit/test_forms_realistic.py.bak
rm staticfiles/css/garden-ui-theme.css.backup
rm static/css/garden-ui-theme.css.backup
```

### Unused JavaScript Files (1 file)
```bash
rm static/js/garden-theme-toggle.js  # No longer used after Alpine.js consolidation
```

### Build Artifacts (can be regenerated)
```bash
rm -rf .django_tailwind_cli/        # 75MB+ Tailwind CLI cache - will regenerate
rm static/css/tailwind.css          # Generated file - will regenerate
```

### Python Cache Files (standard cleanup)
```bash
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name ".DS_Store" -delete
```

## CSS Files Requiring Analysis (56 total)

### Potentially Unused CSS Categories:

1. **Fix/Patch Files** (need investigation):
   - `pricing-features-fix.css`
   - `contact-page-fixes.css` 
   - `responsive-breakpoints-fix.css`
   - `faq-page-fixes.css`

2. **Layer System Files** (architecture decision needed):
   - `layers/18-pricing.css`
   - `layers/27-institutional-page.css`
   - `layers/30-*.css` (multiple)
   - `layers/33-consultation-page.css`
   - `layers/40-adviser-page-clean.css`
   - `layers/43-garden-overview.css`

3. **Consolidated Files** (keep - these are good):
   - `blog-core-consolidated.css` ✅
   - `blog-components-consolidated.css` ✅
   - `blog-consistency-consolidated.css` ✅
   - `accessibility-consolidated.css` ✅

4. **Page-Specific Files** (keep if used):
   - `onboarding-page.css` ✅
   - `process-page.css` ✅
   - `about-page-v2.css` ✅

## Recommendations

### Phase 1: Safe Cleanup (Immediate)
- Delete backup files, unused JS, build artifacts
- Standard Python cache cleanup
- Total space saved: ~80MB+

### Phase 2: CSS Architecture Review (Future)
- Audit which layer files are actually used
- Consolidate fix files into main stylesheets
- Consider migrating more pages to use Tailwind classes directly

### Phase 3: Static Assets Review (Future)  
- Audit unused images, fonts, other static files
- Check for orphaned media files

## Impact Assessment
- **Risk Level**: LOW for Phase 1 (all regeneratable or truly unused)
- **Space Saved**: 80MB+ immediately
- **Maintenance**: Cleaner codebase, fewer files to manage
- **Build Time**: Potentially faster without unused assets
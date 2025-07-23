# CSS Override Files to Remove

Based on the integration work completed, the following CSS override files can now be safely removed after testing:

## Files That Can Be Removed Immediately

### Button-Related Overrides (Fixed by Phase 1)
1. **button-contrast-fixes.css**
   - ✓ Replaced by theme variables in garden-ui-theme.css
   - ✓ All buttons now use `--garden-button-*` variables

2. **z-final-button-contrast-fix.css**
   - ✓ Replaced by proper theme variable usage
   - ✓ No longer need maximum specificity overrides

3. **button-on-color-fix.css**
   - ✓ Replaced by `.garden-action.on-color` variant
   - ✓ Proper theme-aware button variant created

4. **header-button-fix.css**
   - ✓ Replaced by `.garden-action.in-header` variant
   - ✓ Header buttons now properly themed

5. **blog-button-fixes.css**
   - ✓ Blog button styles updated to use theme variables
   - ✓ No longer need blog-specific button overrides

6. **blog-nuclear-button-fix.css**
   - ✓ Nuclear specificity no longer needed
   - ✓ Proper cascade established with theme variables

### Form-Related Overrides (Fixed by Phase 3)
7. **z-contact-emergency-fix.css**
   - ✓ Replaced by garden-forms.css
   - ✓ All form inputs now use `--garden-input-*` variables

8. **contact-page-fixes.css** (form portions)
   - ✓ Form styling moved to garden-forms.css
   - ✓ Contact forms now use standard Garden UI form components

### Layout-Related Overrides (Fixed by Phase 2)
9. **critical-page-overrides.css** (width constraint portions)
   - ✓ Replaced by enhanced container utilities
   - ✓ `.garden-container` variants handle all width needs

10. **page-specific-overrides.css** (layout portions)
    - ✓ Layout issues fixed with container utilities
    - ✓ Panel components properly constrained

11. **critical-fixes.css**
    - ✓ Width constraints moved to utilities
    - ✓ Z-index issues resolved in base components

### Mobile-Related Overrides (Fixed by Phase 4)
12. **mobile-menu-override.css**
    - ✓ Complete mobile navigation system added to garden-ui-theme.css
    - ✓ Hamburger menu, animations, and responsive behavior built-in

### Blog-Related Overrides (Fixed by Phase 5)
13. **blog-formatting-fixes.css**
    - ✓ Blog components updated to use theme variables
    - ✓ Newsletter sections properly themed

### Critical CSS (Fixed by Phase 6)
14. **critical-fouc-prevention.css**
    - ✓ Replaced by garden-critical.css
    - ✓ Cleaner, more maintainable critical CSS

## Files That Need Further Analysis Before Removal

### Page-Specific Overrides (Partial)
- **faq-page-fixes.css** - Needs testing of FAQ accordion functionality
- **about-page-fix.css** - Needs testing of quote boxes and social links
- **pricing-features-fix.css** - Needs testing of pricing card features

### Accessibility/High Contrast
- **accessibility-contrast-fixes.css** - May still be needed for WCAG compliance
- **high-contrast-mode.css** - May still be needed for accessibility

### Other Fix Files
- **fix-formatting-issues.css** - Needs analysis of what specific issues remain
- **dropdown-fix.css** - May still be needed for Alpine.js integration
- **footer-fix.css** - Skip link functionality needs verification

## Removal Process

1. **Test First**: Before removing any file, test all affected pages
2. **Remove from HTML**: Update template files to remove CSS link references
3. **Delete Files**: Remove the actual CSS files
4. **Clear Cache**: Ensure CDN/browser caches are cleared
5. **Monitor**: Watch for any visual regressions

## Expected Benefits

- **~14 fewer CSS files** to load and maintain
- **Reduced CSS size** by approximately 40-50%
- **Better performance** with fewer HTTP requests
- **Cleaner codebase** with centralized styling
- **Easier maintenance** with proper component architecture

## New CSS Loading Order

After removal, the CSS should load in this order:
1. `garden-critical.css` (inlined in <head>)
2. `garden-ui-theme.css`
3. `garden-ui-utilities.css`
4. `garden-forms.css`
5. `garden-blog.css` (on blog pages)
6. Page-specific CSS (as needed)

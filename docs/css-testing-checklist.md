# CSS Integration Testing Checklist

## Pre-Deployment Testing

### 1. Update Base Template
- [ ] Replace `/templates/public_site/base.html` with `/templates/public_site/base_updated.html`
- [ ] Or update the existing base.html with the changes from base_updated.html

### 2. Visual Testing - All Themes

#### Light Theme
- [ ] Header displays correctly (Lavender background)
- [ ] Primary buttons show Tiffany Blue (#7bcdba)
- [ ] Secondary buttons have proper contrast
- [ ] Form inputs have white background
- [ ] Text is readable throughout
- [ ] Mobile menu works properly

#### Dark Theme
- [ ] Header displays correctly (Dark purple #1f0322)
- [ ] Primary buttons show Maya Blue (#55c1ff)
- [ ] Secondary buttons have proper contrast
- [ ] Form inputs have dark background
- [ ] Text is readable throughout
- [ ] Mobile menu works properly

#### Auto Theme
- [ ] Switches properly based on system preference
- [ ] Time-based switching works (6AM/8PM)

### 3. Component Testing

#### Buttons
- [ ] Primary buttons - all states (normal, hover, focus, disabled)
- [ ] Secondary buttons - all states
- [ ] Buttons on colored backgrounds (.on-color variant)
- [ ] Header buttons (.in-header variant)
- [ ] Blog buttons
- [ ] CTA buttons in hero sections

#### Forms
- [ ] Text inputs - all states (normal, focus, error, disabled)
- [ ] Textareas
- [ ] Select dropdowns
- [ ] Checkboxes and radio buttons
- [ ] Form validation states
- [ ] Newsletter signup forms

#### Layout
- [ ] Container widths (narrow, normal, wide)
- [ ] Panel components don't overflow
- [ ] Content properly constrained
- [ ] Responsive behavior at all breakpoints

#### Mobile Navigation
- [ ] Hamburger menu visible on mobile
- [ ] Menu slides in/out properly
- [ ] Overlay works
- [ ] Desktop nav hidden on mobile
- [ ] Mobile nav hidden on desktop

### 4. Page-Specific Testing

#### Homepage
- [ ] Hero section buttons
- [ ] Service cards
- [ ] All CTAs visible and clickable

#### Blog Pages
- [ ] Article list layout
- [ ] Blog sidebar
- [ ] Newsletter signup
- [ ] Tags and categories
- [ ] Social links

#### Contact Page
- [ ] Contact form styling
- [ ] Input fields work properly
- [ ] Submit button visible

#### About/FAQ/Pricing Pages
- [ ] Content layout
- [ ] Interactive elements
- [ ] Page-specific components

### 5. Accessibility Testing

- [ ] Keyboard navigation works
- [ ] Focus states visible
- [ ] Skip links functional
- [ ] Screen reader compatibility
- [ ] Color contrast meets WCAG AA

### 6. Performance Testing

- [ ] Page load time improved
- [ ] No CSS loading errors in console
- [ ] No visual flashing (FOUC)
- [ ] Critical CSS prevents layout shift

### 7. Browser Testing

- [ ] Chrome/Edge
- [ ] Firefox
- [ ] Safari
- [ ] Mobile browsers (iOS Safari, Chrome Android)

### 8. Final Checks

- [ ] No JavaScript errors in console
- [ ] Theme switching works properly
- [ ] All interactive elements functional
- [ ] No visual regressions from original

## Deployment Steps

1. **Test in Development**
   - Use the updated base template
   - Test all items above

2. **Deploy to Staging**
   - Update base template
   - Run collectstatic
   - Test again in staging environment

3. **Production Deployment**
   - Deploy during low traffic
   - Update base template
   - Run collectstatic
   - Clear CDN cache
   - Monitor for issues

4. **Post-Deployment**
   - Run the remove-old-css-files.sh script
   - Verify site still works
   - Monitor error logs
   - Be ready to rollback if needed

## Rollback Plan

If issues are found:

1. Revert base.html to original version
2. Restore CSS files from backup directory
3. Clear caches
4. Investigate and fix issues before retry

## Success Criteria

- [ ] All visual elements match original design
- [ ] No functionality broken
- [ ] Performance improved
- [ ] No console errors
- [ ] Positive user feedback

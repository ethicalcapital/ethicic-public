# WCAG Contrast Audit Report - Ethical Capital Website

**Date:** 2025-07-12
**Auditor:** Claude Code
**Focus:** WCAG AA contrast compliance, with special attention to purple text on gray backgrounds

## Executive Summary

The audit revealed several contrast issues that fail WCAG AA standards (4.5:1 for normal text, 3:1 for large text). While most purple text elements on the website actually pass contrast requirements, there are critical failures in both light and dark modes that need immediate attention.

### Key Findings:
1. **Purple text on gray backgrounds**: Most instances PASS contrast requirements (11.49:1 to 12:1 ratio)
2. **Critical failures**: Header button elements have extremely poor contrast (1:1 ratio)
3. **Dark mode issues**: Purple links (`policy-link` class) become nearly invisible in dark mode
4. **Total unique issues**: 10 contrast combinations failing WCAG AA

## Detailed Findings

### Light Mode Issues

#### 1. CRITICAL: Header Button Elements (1:1 ratio) ❌
- **Elements**: Search button, Login button, Theme toggle
- **Colors**: `rgb(255, 255, 255)` on `rgba(255, 255, 255, 0.15)`
- **Current ratio**: 1:1 (Required: 4.5:1)
- **Impact**: These buttons are nearly invisible
- **Affected selectors**:
  - `button.garden-search-btn`
  - `button.garden-login-btn`
  - `button.garden-theme-toggle`

#### 2. Banner Text (1.05:1 ratio) ❌
- **Element**: "LIMITED QUARTERLY OPENINGS" banner
- **Colors**: `rgb(255, 255, 255)` on `rgb(249, 250, 251)`
- **Current ratio**: 1.05:1 (Required: 4.5:1)
- **Impact**: Banner text is nearly invisible
- **Affected selector**: `div.accepting-clients-banner`

#### 3. Statistics Fill Element (1.57:1 ratio) ❌
- **Element**: Progress bar fill
- **Colors**: `rgb(17, 17, 17)` on `rgb(61, 41, 112)`
- **Current ratio**: 1.57:1 (Required: 4.5:1)
- **Impact**: Dark text on dark purple background

### Purple Text on Gray - PASSING ✅

Despite the user's concern, most purple text on gray backgrounds actually PASSES WCAG AA:

#### On White Background (12:1 ratio) ✅
- All purple headings (`h2`, `h3`, `h4`)
- Purple links (`a.policy-link`)
- Section titles
- **Colors**: `rgb(61, 41, 112)` on `rgb(255, 255, 255)`

#### On Light Gray Background (11.49:1 ratio) ✅
- Statistics numbers
- Call-to-action links
- Strong/bold text elements
- **Colors**: `rgb(61, 41, 112)` on `rgb(249, 250, 251)`

### Dark Mode Issues

#### 1. CRITICAL: Purple Links Become Invisible (1.05:1 - 1.57:1 ratio) ❌
- **Elements**: Policy links remain purple but background becomes dark
- **Colors**: `rgb(61, 41, 112)` on `rgb(51, 51, 51)` or `rgb(17, 17, 17)`
- **Current ratio**: 1.05:1 to 1.57:1 (Required: 4.5:1)
- **Impact**: Links are completely unreadable in dark mode
- **Affected selectors**: `a.policy-link`

## Recommendations

### Immediate Actions Required:

1. **Fix Header Buttons**
   - Change button background from `rgba(255, 255, 255, 0.15)` to a darker color
   - Or change text color to ensure 4.5:1 contrast ratio
   - Suggested: Use purple background with white text

2. **Fix Banner Visibility**
   - Change banner background to provide adequate contrast
   - Or use dark text on light background
   - Suggested: Use brand purple for banner background

3. **Fix Dark Mode Purple Links**
   - Purple links must change color in dark mode
   - Suggested: Use a lighter purple (#9B8BDB) or white for links in dark mode
   - This is a critical accessibility failure

### CSS Variables to Review:

Based on the audit, these color combinations need adjustment:
- Header button colors
- Banner background colors
- Dark mode link colors (especially for `.policy-link`)

### Testing Recommendations:

1. Use automated contrast checking tools in development
2. Test all color combinations in both light and dark modes
3. Consider using CSS custom properties for theme-aware colors
4. Implement a contrast checking tool in your CI/CD pipeline

## Summary

While the concern about purple text on gray backgrounds was mostly unfounded (these combinations actually have excellent contrast), the audit revealed other critical contrast failures that need immediate attention. The most severe issues are:

1. Header navigation buttons (1:1 ratio)
2. Banner text visibility (1.05:1 ratio)
3. Dark mode purple links (1.05:1 to 1.57:1 ratio)

These issues make important UI elements and content invisible or very difficult to read, creating significant accessibility barriers for users with visual impairments.
